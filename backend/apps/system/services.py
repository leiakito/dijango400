"""
系统服务
"""
import os
import subprocess
import gzip
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from .models import BackupJob, SysLog
from .middleware import log_system_event


class BackupService:
    """数据库备份服务"""
    
    def __init__(self):
        self.backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def create_backup(self):
        """
        创建数据库备份
        返回: BackupJob 实例
        """
        backup_job = BackupJob.objects.create(
            status=BackupJob.Status.RUNNING
        )
        
        try:
            # 生成备份文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'backup_{timestamp}.sql.gz'
            file_path = os.path.join(self.backup_dir, filename)
            
            # 执行备份
            self._execute_backup(file_path)
            
            # 获取文件大小
            file_size = os.path.getsize(file_path)
            
            # 更新任务状态
            backup_job.status = BackupJob.Status.SUCCESS
            backup_job.file_path = file_path
            backup_job.file_size = file_size
            backup_job.finished_at = timezone.now()
            backup_job.save()
            
            # 记录日志
            log_system_event(
                level=SysLog.Level.INFO,
                module='backup',
                message=f'数据库备份成功: {filename}',
                context={
                    'file_path': file_path,
                    'file_size': file_size
                }
            )
            
            # 清理旧备份
            self._cleanup_old_backups()
            
        except Exception as e:
            # 备份失败
            backup_job.status = BackupJob.Status.FAILED
            backup_job.error_message = str(e)
            backup_job.finished_at = timezone.now()
            backup_job.save()
            
            # 记录错误日志
            log_system_event(
                level=SysLog.Level.ERROR,
                module='backup',
                message=f'数据库备份失败: {str(e)}',
                context={'error': str(e)}
            )
        
        return backup_job
    
    def _execute_backup(self, file_path):
        """执行数据库备份命令"""
        db_config = settings.DATABASES['default']
        
        # 提取数据库配置
        db_name = db_config['NAME']
        db_user = db_config['USER']
        db_password = db_config['PASSWORD']
        db_host = db_config.get('HOST', 'localhost')
        db_port = db_config.get('PORT', '3306')
        
        # 使用环境变量传递密码，避免命令行警告
        env = os.environ.copy()
        env['MYSQL_PWD'] = db_password
        
        # 构建mysqldump命令（不在命令行中包含密码）
        dump_cmd = [
            'mysqldump',
            f'--host={db_host}',
            f'--port={db_port}',
            f'--user={db_user}',
            '--single-transaction',
            '--quick',
            '--lock-tables=false',
            db_name
        ]
        
        # 执行备份并压缩
        try:
            # 执行mysqldump
            dump_process = subprocess.Popen(
                dump_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env
            )
            
            # 压缩并保存
            with gzip.open(file_path, 'wb') as f:
                for line in dump_process.stdout:
                    f.write(line)
            
            # 等待进程完成
            dump_process.wait()
            
            # 检查返回码
            if dump_process.returncode != 0:
                stderr = dump_process.stderr.read().decode('utf-8')
                # 过滤掉密码警告
                if 'Using a password on the command line' not in stderr:
                    raise Exception(stderr)
            
            # 验证备份文件是否创建且不为空
            if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
                raise Exception('备份文件创建失败或为空')
        
        except FileNotFoundError:
            raise Exception('mysqldump命令未找到，请确保MySQL客户端已安装')
        except Exception as e:
            # 删除可能创建的空文件
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass
            raise Exception(f'备份执行失败: {str(e)}')
    
    def _cleanup_old_backups(self):
        """清理旧备份文件"""
        from .models import SysConfig
        
        # 获取配置的保留数量
        retention_count = int(SysConfig.get_value('system.backup.retention_count', 7))
        
        # 获取所有成功的备份，按时间倒序
        successful_backups = BackupJob.objects.filter(
            status=BackupJob.Status.SUCCESS
        ).order_by('-started_at')
        
        # 删除超过保留数量的备份
        backups_to_delete = successful_backups[retention_count:]
        
        for backup in backups_to_delete:
            try:
                # 删除文件
                if backup.file_path and os.path.exists(backup.file_path):
                    os.remove(backup.file_path)
                
                # 删除记录
                backup.delete()
                
                log_system_event(
                    level=SysLog.Level.INFO,
                    module='backup',
                    message=f'清理旧备份: {backup.file_path}'
                )
            except Exception as e:
                log_system_event(
                    level=SysLog.Level.WARNING,
                    module='backup',
                    message=f'清理备份失败: {str(e)}',
                    context={'backup_id': backup.id, 'error': str(e)}
                )


class LogService:
    """日志服务"""
    
    @staticmethod
    def cleanup_old_logs(days=30):
        """
        清理旧日志
        
        Args:
            days: 保留最近多少天的日志
        
        Returns:
            删除的日志数量
        """
        from datetime import timedelta
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        deleted_count, _ = SysLog.objects.filter(
            created_at__lt=cutoff_date
        ).delete()
        
        # 记录清理日志
        log_system_event(
            level=SysLog.Level.INFO,
            module='log_cleanup',
            message=f'清理了 {deleted_count} 条旧日志（{days}天前）',
            context={'days': days, 'deleted_count': deleted_count}
        )
        
        return deleted_count


# 创建全局实例
backup_service = BackupService()
log_service = LogService()

