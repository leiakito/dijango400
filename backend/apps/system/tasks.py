"""
系统定时任务
"""
from celery import shared_task
from .services import backup_service, log_service
from .models import SysConfig, SysLog
from .middleware import log_system_event


@shared_task(name='system.auto_backup')
def auto_backup():
    """
    自动备份任务
    根据系统配置执行数据库备份
    """
    try:
        # 检查是否启用自动备份
        auto_enabled = SysConfig.get_value('system.backup.auto_enabled', 'false')
        if auto_enabled.lower() != 'true':
            return '自动备份未启用'
        
        # 执行备份
        backup_job = backup_service.create_backup()
        
        if backup_job.status == 'success':
            return f'自动备份成功: {backup_job.file_path}'
        else:
            return f'自动备份失败: {backup_job.error_message}'
    
    except Exception as e:
        error_msg = f'自动备份任务异常: {str(e)}'
        log_system_event(
            level=SysLog.Level.ERROR,
            module='backup_task',
            message=error_msg
        )
        return error_msg


@shared_task(name='system.auto_cleanup_logs')
def auto_cleanup_logs():
    """
    自动清理日志任务
    根据系统配置清理过期日志
    """
    try:
        # 获取配置的保留天数
        retention_days = int(SysConfig.get_value('system.log.retention_days', '30'))
        
        # 执行清理
        deleted_count = log_service.cleanup_old_logs(retention_days)
        
        return f'自动清理日志完成: 删除 {deleted_count} 条记录'
    
    except Exception as e:
        error_msg = f'自动清理日志任务异常: {str(e)}'
        log_system_event(
            level=SysLog.Level.ERROR,
            module='log_cleanup_task',
            message=error_msg
        )
        return error_msg


@shared_task(name='system.health_check')
def health_check():
    """
    系统健康检查任务
    定期检查系统各组件状态
    """
    try:
        from django.db import connection
        from django.core.cache import cache
        
        issues = []
        
        # 检查数据库
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        except Exception as e:
            issues.append(f'数据库异常: {str(e)}')
        
        # 检查缓存
        try:
            cache_key = 'health_check_task'
            cache.set(cache_key, 'ok', 10)
            if cache.get(cache_key) != 'ok':
                issues.append('缓存读写异常')
        except Exception as e:
            issues.append(f'缓存异常: {str(e)}')
        
        # 记录日志
        if issues:
            log_system_event(
                level=SysLog.Level.WARNING,
                module='health_check',
                message='系统健康检查发现问题',
                context={'issues': issues}
            )
            return f'发现 {len(issues)} 个问题'
        else:
            return '系统健康'
    
    except Exception as e:
        error_msg = f'健康检查任务异常: {str(e)}'
        log_system_event(
            level=SysLog.Level.ERROR,
            module='health_check',
            message=error_msg
        )
        return error_msg
