"""
Games app configuration
"""
from django.apps import AppConfig


class GamesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.games'
    verbose_name = '游戏管理'

    def ready(self):
        """
        应用启动时执行的操作
        """
        # 导入信号处理器(如果有)
        # import apps.games.signals
        
        # 自动导入游戏数据
        self.auto_import_game_data()
    
    def auto_import_game_data(self):
        """
        自动导入游戏数据(仅在数据库为空时)
        """
        import os
        import json
        from django.conf import settings
        from django.db import connection
        
        # 检查是否在运行迁移或其他管理命令
        import sys
        if 'migrate' in sys.argv or 'makemigrations' in sys.argv:
            return
        
        try:
            # 检查数据库表是否存在
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) FROM information_schema.tables "
                    "WHERE table_schema = DATABASE() AND table_name = 'games'"
                )
                if cursor.fetchone()[0] == 0:
                    return  # 表不存在,跳过
            
            # 延迟导入模型,避免AppRegistryNotReady错误
            from apps.games.models import Game, Publisher, Tag
            
            # 检查是否已有数据
            if Game.objects.exists():
                return  # 已有数据,不重复导入
            
            # 读取JSON文件
            json_file = os.path.join(settings.BASE_DIR, 'game_data.json')
            if not os.path.exists(json_file):
                return  # 文件不存在
            
            print('检测到数据库为空,正在自动导入游戏数据...')
            
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 导入数据
            from apps.games.utils import import_game_data
            import_game_data(data)
            
            print('游戏数据导入完成!')
            
        except Exception as e:
            # 静默处理错误,避免影响应用启动
            print(f'自动导入游戏数据时出错: {e}')
