"""
System Views - 系统管理模块视图
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from config.permissions import IsAdmin
from django.db.models import Count
from datetime import datetime, timedelta

from .models import SysConfig, SysLog, BackupJob
from .serializers import (
    SysConfigSerializer, SysLogSerializer, BackupJobSerializer
)


class SysConfigViewSet(viewsets.ModelViewSet):
    """
    系统配置视图集
    """
    queryset = SysConfig.objects.all()
    serializer_class = SysConfigSerializer
    permission_classes = [IsAdmin]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['key', 'description']
    ordering = ['key']
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def public(self, request):
        """获取公开配置"""
        configs = SysConfig.objects.filter(is_public=True)
        serializer = self.get_serializer(configs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def batch_update(self, request):
        """批量更新配置"""
        configs_data = request.data.get('configs', [])
        
        updated_count = 0
        errors = []
        
        for config_data in configs_data:
            key = config_data.get('key')
            value = config_data.get('value')
            description = config_data.get('description', '')
            
            if not key:
                errors.append('配置键不能为空')
                continue
            
            if value is None:
                errors.append(f'配置 {key} 的值不能为空')
                continue
            
            try:
                # 更新或创建配置
                config = SysConfig.set_value(key, str(value), description)
                updated_count += 1
            except Exception as e:
                errors.append(f'更新配置 {key} 失败: {str(e)}')
        
        # 记录系统日志
        if updated_count > 0:
            from apps.system.middleware import log_system_event
            log_system_event(
                level='INFO',
                module='system',
                message=f"批量更新系统配置 ({updated_count}项)",
                context={
                    'updated_count': updated_count,
                    'operator': request.user.username,
                    'configs': [c.get('key') for c in configs_data if c.get('key')]
                },
                user=request.user
            )
        
        response_data = {
            'message': f'成功更新 {updated_count} 个配置',
            'updated_count': updated_count
        }
        
        if errors:
            response_data['errors'] = errors
        
        return Response(response_data)


class SysLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    系统日志视图集（只读）
    """
    queryset = SysLog.objects.all()
    serializer_class = SysLogSerializer
    permission_classes = [IsAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['level', 'module', 'user']
    search_fields = ['message', 'module']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取日志统计信息"""
        # 按日志级别统计
        level_stats = SysLog.objects.values('level').annotate(count=Count('id'))
        
        # 最近24小时日志数量
        last_24h = SysLog.objects.filter(
            created_at__gte=datetime.now() - timedelta(hours=24)
        ).count()
        
        # 按模块统计（Top 10）
        module_stats = SysLog.objects.values('module').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        stats = {
            'total': SysLog.objects.count(),
            'last_24h': last_24h,
            'by_level': {item['level']: item['count'] for item in level_stats},
            'top_modules': list(module_stats)
        }
        
        return Response(stats)
    
    @action(detail=False, methods=['post'])
    def cleanup(self, request):
        """清理旧日志"""
        from .services import log_service
        
        days = request.data.get('days', 30)
        
        try:
            days = int(days)
            if days < 1:
                return Response(
                    {'error': '天数必须大于0'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (ValueError, TypeError):
            return Response(
                {'error': '无效的天数参数'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        deleted_count = log_service.cleanup_old_logs(days)
        
        # 记录系统日志（清理日志本身也要记录）
        from apps.system.middleware import log_system_event
        log_system_event(
            level='INFO',
            module='system',
            message=f"清理过期日志 ({deleted_count}条)",
            context={
                'deleted_count': deleted_count,
                'retention_days': days,
                'operator': request.user.username
            },
            user=request.user
        )
        
        return Response({
            'message': f'成功清理 {deleted_count} 条日志',
            'deleted_count': deleted_count
        })


class BackupJobViewSet(viewsets.ReadOnlyModelViewSet):
    """
    备份任务视图集
    """
    queryset = BackupJob.objects.all()
    serializer_class = BackupJobSerializer
    permission_classes = [IsAdmin]
    ordering = ['-started_at']
    
    @action(detail=False, methods=['post'])
    def create_backup(self, request):
        """创建新的备份任务"""
        from .services import backup_service
        
        # 检查是否有正在运行的备份任务
        running_jobs = BackupJob.objects.filter(
            status=BackupJob.Status.RUNNING
        )
        
        if running_jobs.exists():
            # 清理可能卡住的任务（超过10分钟的running状态）
            from datetime import timedelta
            cutoff_time = timezone.now() - timedelta(minutes=10)
            stuck_jobs = running_jobs.filter(started_at__lt=cutoff_time)
            
            if stuck_jobs.exists():
                stuck_jobs.update(
                    status=BackupJob.Status.FAILED,
                    error_message='任务超时，已自动标记为失败',
                    finished_at=timezone.now()
                )
            else:
                return Response(
                    {'error': '已有备份任务正在运行，请稍后再试'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # 创建备份（同步执行，实际项目中应该使用Celery异步执行）
        try:
            backup_job = backup_service.create_backup()
            serializer = self.get_serializer(backup_job)
            
            # 记录系统日志
            from apps.system.middleware import log_system_event
            if backup_job.status == BackupJob.Status.SUCCESS:
                log_system_event(
                    level='INFO',
                    module='backup',
                    message=f"数据库备份成功",
                    context={
                        'backup_id': backup_job.id,
                        'file_path': backup_job.file_path,
                        'file_size': backup_job.file_size,
                        'duration': backup_job.duration,
                        'operator': request.user.username
                    },
                    user=request.user
                )
                return Response({
                    'message': '备份创建成功',
                    'job': serializer.data
                })
            else:
                log_system_event(
                    level='ERROR',
                    module='backup',
                    message=f"数据库备份失败: {backup_job.error_message}",
                    context={
                        'backup_id': backup_job.id,
                        'error': backup_job.error_message,
                        'operator': request.user.username
                    },
                    user=request.user
                )
                return Response({
                    'message': '备份失败',
                    'error': backup_job.error_message,
                    'job': serializer.data
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        except Exception as e:
            return Response({
                'error': f'备份失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SystemHealthViewSet(viewsets.ViewSet):
    """
    系统健康检查视图集
    """
    permission_classes = [IsAdmin]
    
    def list(self, request):
        """获取系统健康状态"""
        from django.db import connection
        from django.core.cache import cache
        import sys
        import platform
        
        health_data = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'checks': {}
        }
        
        # 数据库检查
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            health_data['checks']['database'] = {
                'status': 'ok',
                'message': '数据库连接正常'
            }
        except Exception as e:
            health_data['checks']['database'] = {
                'status': 'error',
                'message': str(e)
            }
            health_data['status'] = 'unhealthy'
        
        # 缓存检查
        try:
            cache_key = 'health_check'
            cache.set(cache_key, 'ok', 10)
            cache_value = cache.get(cache_key)
            if cache_value == 'ok':
                health_data['checks']['cache'] = {
                    'status': 'ok',
                    'message': '缓存系统正常'
                }
            else:
                health_data['checks']['cache'] = {
                    'status': 'warning',
                    'message': '缓存读写异常'
                }
        except Exception as e:
            health_data['checks']['cache'] = {
                'status': 'error',
                'message': str(e)
            }
        
        # 系统信息
        health_data['system_info'] = {
            'python_version': sys.version,
            'platform': platform.platform(),
            'processor': platform.processor()
        }
        
        return Response(health_data)

