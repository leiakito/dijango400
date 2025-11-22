"""
Celery configuration for game platform
"""
import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')

app = Celery('game_platform')

# Load config from Django settings with CELERY namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all installed apps
app.autodiscover_tasks()

# Celery Beat Schedule - 定时任务
app.conf.beat_schedule = {
    # 每日凌晨2点执行爬虫任务
    'crawl-external-data': {
        'task': 'apps.analytics.tasks.crawl_external_data',
        'schedule': crontab(hour=2, minute=0),
        'options': {'queue': 'crawl'}
    },
    # 每日凌晨3点计算热度
    'calculate-game-heat': {
        'task': 'apps.analytics.tasks.calculate_game_heat',
        'schedule': crontab(hour=3, minute=0),
        'options': {'queue': 'analytics'}
    },
    # 每日凌晨3点30分生成推荐
    'generate-recommendations': {
        'task': 'apps.recommendations.tasks.generate_all_recommendations',
        'schedule': crontab(hour=3, minute=30),
        'options': {'queue': 'recommendations'}
    },
    # 每小时更新话题热度
    'update-topic-heat': {
        'task': 'apps.community.tasks.update_topic_heat',
        'schedule': crontab(minute=0),
        'options': {'queue': 'community'}
    },
    # 每日凌晨2点执行数据库备份
    'auto-backup-database': {
        'task': 'system.auto_backup',
        'schedule': crontab(hour=2, minute=0),
        'options': {'queue': 'system'}
    },
    # 每日凌晨1点清理旧日志
    'auto-cleanup-logs': {
        'task': 'system.auto_cleanup_logs',
        'schedule': crontab(hour=1, minute=0),
        'options': {'queue': 'system'}
    },
    # 每15分钟进行一次健康检查
    'health-check': {
        'task': 'system.health_check',
        'schedule': crontab(minute='*/15'),
        'options': {'queue': 'system'}
    },
    # 每5分钟同步单机游戏排行榜
    'sync-single-player-ranking': {
        'task': 'apps.games.tasks.sync_single_player_ranking',
        'schedule': crontab(minute='*/5'),
        'options': {'queue': 'analytics'}
    },
}

# Task routing
app.conf.task_routes = {
    'apps.analytics.tasks.*': {'queue': 'analytics'},
    'apps.recommendations.tasks.*': {'queue': 'recommendations'},
    'apps.community.tasks.*': {'queue': 'community'},
    'apps.system.tasks.*': {'queue': 'system'},
    'apps.games.tasks.*': {'queue': 'analytics'},
}

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task for testing"""
    print(f'Request: {self.request!r}')
