"""
数据库备份脚本
"""
import os
import sys
import django
from datetime import datetime
import subprocess

# 设置 Django 环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.prod')
django.setup()

from django.conf import settings


def backup_database():
    """
    执行数据库备份
    """
    # 解析数据库配置
    db_config = settings.DATABASES['default']
    
    # 创建备份目录
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    
    # 生成备份文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(backup_dir, f'backup_{timestamp}.sql')
    
    # 构建 mysqldump 命令
    host = db_config.get('HOST', 'localhost')
    port = db_config.get('PORT', 3306)
    user = db_config.get('USER', 'root')
    password = db_config.get('PASSWORD', '')
    database = db_config.get('NAME')
    
    cmd = [
        'mysqldump',
        f'--host={host}',
        f'--port={port}',
        f'--user={user}',
        f'--password={password}',
        '--single-transaction',
        '--quick',
        '--lock-tables=false',
        database
    ]
    
    # 执行备份
    with open(backup_file, 'w') as f:
        result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
    
    if result.returncode != 0:
        raise Exception(f"Backup failed: {result.stderr}")
    
    # 获取文件大小
    file_size = os.path.getsize(backup_file)
    
    print(f"Backup completed: {backup_file} ({file_size} bytes)")
    
    return backup_file, file_size


def restore_database(backup_file):
    """
    恢复数据库
    """
    if not os.path.exists(backup_file):
        raise FileNotFoundError(f"Backup file not found: {backup_file}")
    
    # 解析数据库配置
    db_config = settings.DATABASES['default']
    
    host = db_config.get('HOST', 'localhost')
    port = db_config.get('PORT', 3306)
    user = db_config.get('USER', 'root')
    password = db_config.get('PASSWORD', '')
    database = db_config.get('NAME')
    
    cmd = [
        'mysql',
        f'--host={host}',
        f'--port={port}',
        f'--user={user}',
        f'--password={password}',
        database
    ]
    
    # 执行恢复
    with open(backup_file, 'r') as f:
        result = subprocess.run(cmd, stdin=f, stderr=subprocess.PIPE, text=True)
    
    if result.returncode != 0:
        raise Exception(f"Restore failed: {result.stderr}")
    
    print(f"Database restored from: {backup_file}")
    
    return True


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'restore':
        if len(sys.argv) < 3:
            print("Usage: python db_backup.py restore <backup_file>")
            sys.exit(1)
        
        backup_file = sys.argv[2]
        restore_database(backup_file)
    else:
        backup_database()

