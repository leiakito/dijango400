"""
Django管理命令: 从JSON文件导入游戏数据
使用方法: python manage.py load_game_data
"""
import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.games.models import Publisher, Tag, Game
from apps.games.utils import import_game_data, check_duplicate_games, remove_duplicate_games


class Command(BaseCommand):
    help = '从game_data.json文件导入游戏数据到数据库'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='game_data.json',
            help='JSON数据文件路径(默认: game_data.json)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='导入前清空现有数据'
        )
        parser.add_argument(
            '--check-duplicates',
            action='store_true',
            help='检查重复数据'
        )
        parser.add_argument(
            '--remove-duplicates',
            action='store_true',
            help='删除重复数据'
        )

    def handle(self, *args, **options):
        # 检查重复数据
        if options['check_duplicates']:
            self.stdout.write('正在检查重复数据...')
            duplicates = check_duplicate_games()
            if duplicates:
                self.stdout.write(self.style.WARNING(
                    f'发现 {len(duplicates)} 个重复游戏:'
                ))
                for name in duplicates:
                    count = Game.objects.filter(name=name).count()
                    self.stdout.write(f'  - {name} (重复 {count} 次)')
            else:
                self.stdout.write(self.style.SUCCESS('未发现重复数据'))
            return
        
        # 删除重复数据
        if options['remove_duplicates']:
            self.stdout.write('正在删除重复数据...')
            deleted = remove_duplicate_games()
            self.stdout.write(self.style.SUCCESS(f'已删除 {deleted} 个重复游戏'))
            return
        
        # 导入数据
        file_path = options['file']
        
        # 如果是相对路径,从backend目录开始
        if not os.path.isabs(file_path):
            file_path = os.path.join(settings.BASE_DIR, file_path)
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'文件不存在: {file_path}'))
            return
        
        # 读取JSON数据
        self.stdout.write(f'正在读取文件: {file_path}')
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 清空现有数据(如果指定)
        if options['clear']:
            self.stdout.write(self.style.WARNING('正在清空现有数据...'))
            Game.objects.all().delete()
            Tag.objects.all().delete()
            Publisher.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('现有数据已清空'))
        
        # 使用工具函数导入数据
        self.stdout.write('\n开始导入数据...')
        stats = import_game_data(data)
        
        # 统计信息
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('数据导入完成!'))
        self.stdout.write(f'发行商: 创建 {stats["publishers_created"]}个, 已存在 {stats["publishers_updated"]}个')
        self.stdout.write(f'标签: 创建 {stats["tags_created"]}个, 已存在 {stats["tags_updated"]}个')
        self.stdout.write(f'游戏: 创建 {stats["games_created"]}个, 更新 {stats["games_updated"]}个')
        self.stdout.write(f'\n总计:')
        self.stdout.write(f'  - 发行商: {Publisher.objects.count()}个')
        self.stdout.write(f'  - 标签: {Tag.objects.count()}个')
        self.stdout.write(f'  - 游戏: {Game.objects.count()}个')
        self.stdout.write('='*50)

