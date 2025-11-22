"""
游戏数据导入工具函数
"""
import os
from datetime import datetime
from django.conf import settings
from django.core.files import File
from apps.games.models import Publisher, Tag, Game


def import_game_data(data):
    """
    从字典数据导入游戏信息到数据库
    
    Args:
        data: 包含publishers, tags, games的字典
    
    Returns:
        dict: 导入统计信息
    """
    stats = {
        'publishers_created': 0,
        'publishers_updated': 0,
        'tags_created': 0,
        'tags_updated': 0,
        'games_created': 0,
        'games_updated': 0,
    }
    
    # 默认封面图片路径
    default_cover = 'games/covers/half.jpg'
    default_cover_path = os.path.join(settings.MEDIA_ROOT, default_cover)
    
    # 1. 导入发行商
    publishers = {}
    for pub_data in data.get('publishers', []):
        publisher, created = Publisher.objects.get_or_create(
            name=pub_data['name'],
            defaults={
                'contact_info': pub_data.get('contact_info', ''),
                'description': pub_data.get('description', ''),
                'website': pub_data.get('website', ''),
            }
        )
        publishers[pub_data['name']] = publisher
        if created:
            stats['publishers_created'] += 1
            print(f'  ✓ 创建发行商: {publisher.name}')
        else:
            stats['publishers_updated'] += 1
    
    # 2. 导入标签
    tags = {}
    for tag_data in data.get('tags', []):
        tag, created = Tag.objects.get_or_create(
            name=tag_data['name'],
            defaults={
                'description': tag_data.get('description', ''),
            }
        )
        tags[tag_data['name']] = tag
        if created:
            stats['tags_created'] += 1
            print(f'  ✓ 创建标签: {tag.name}')
        else:
            stats['tags_updated'] += 1
    
    # 3. 导入游戏
    for game_data in data.get('games', []):
        # 获取发行商
        publisher_name = game_data['publisher']
        if publisher_name not in publishers:
            print(f'  ✗ 跳过游戏 {game_data["name"]}: 发行商不存在')
            continue
        
        # 解析日期
        release_date = None
        if game_data.get('release_date'):
            try:
                release_date = datetime.strptime(
                    game_data['release_date'], '%Y-%m-%d'
                ).date()
            except ValueError:
                pass
        
        # 检查游戏是否已存在
        existing_game = Game.objects.filter(name=game_data['name']).first()
        
        if existing_game:
            # 更新现有游戏
            existing_game.category = game_data['category']
            existing_game.publisher = publishers[publisher_name]
            existing_game.rating = game_data.get('rating', 0.0)
            existing_game.download_count = game_data.get('download_count', 0)
            existing_game.follow_count = game_data.get('follow_count', 0)
            existing_game.review_count = game_data.get('review_count', 0)
            existing_game.release_date = release_date
            existing_game.version = game_data.get('version', '')
            existing_game.description = game_data.get('description', '')
            existing_game.heat_static = game_data.get('heat_static', 0.0)
            existing_game.heat_dynamic = game_data.get('heat_dynamic', 0.0)
            existing_game.heat_total = game_data.get('heat_total', 0.0)
            
            # 如果没有封面图,设置默认封面
            if not existing_game.cover_image and os.path.exists(default_cover_path):
                existing_game.cover_image = default_cover
            
            existing_game.save()
            game = existing_game
            stats['games_updated'] += 1
            print(f'  ↻ 更新游戏: {game.name}')
        else:
            # 创建新游戏
            game = Game.objects.create(
                name=game_data['name'],
                category=game_data['category'],
                publisher=publishers[publisher_name],
                rating=game_data.get('rating', 0.0),
                download_count=game_data.get('download_count', 0),
                follow_count=game_data.get('follow_count', 0),
                review_count=game_data.get('review_count', 0),
                release_date=release_date,
                version=game_data.get('version', ''),
                description=game_data.get('description', ''),
                heat_static=game_data.get('heat_static', 0.0),
                heat_dynamic=game_data.get('heat_dynamic', 0.0),
                heat_total=game_data.get('heat_total', 0.0),
            )
            
            # 设置默认封面图
            if os.path.exists(default_cover_path):
                game.cover_image = default_cover
                game.save()
            
            stats['games_created'] += 1
            print(f'  ✓ 创建游戏: {game.name}')
        
        # 添加标签
        game_tags = []
        for tag_name in game_data.get('tags', []):
            if tag_name in tags:
                game_tags.append(tags[tag_name])
        
        if game_tags:
            game.tags.set(game_tags)
    
    return stats


def check_duplicate_games():
    """
    检查数据库中的重复游戏
    
    Returns:
        list: 重复游戏名称列表
    """
    from django.db.models import Count
    
    duplicates = Game.objects.values('name').annotate(
        count=Count('id')
    ).filter(count__gt=1)
    
    return [dup['name'] for dup in duplicates]


def remove_duplicate_games():
    """
    删除重复的游戏,保留最新的一个
    
    Returns:
        int: 删除的游戏数量
    """
    duplicate_names = check_duplicate_games()
    deleted_count = 0
    
    for name in duplicate_names:
        games = Game.objects.filter(name=name).order_by('-created_at')
        # 保留第一个(最新的),删除其他的
        for game in games[1:]:
            game.delete()
            deleted_count += 1
            print(f'删除重复游戏: {name} (ID: {game.id})')
    
    return deleted_count

