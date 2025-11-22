"""
数据分析服务
处理爬虫数据、计算指标、生成可视化数据
"""
import pandas as pd
import hashlib
import json
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Count, Sum, Avg, Q
from django.core.cache import cache
from .models import RawCrawl, DashCardCache, CrawlJob
from apps.games.models import Game, Publisher, Tag
from apps.recommendations.models import GameMetricsDaily
from apps.community.models import Post, Comment
import logging

logger = logging.getLogger(__name__)


class AnalyticsService:
    """数据分析服务类"""
    
    def process_crawled_data(self, source, data_list):
        """
        处理爬取的原始数据
        去重、清洗、入库
        """
        processed_count = 0
        
        for data in data_list:
            try:
                # 计算数据哈希用于去重
                data_str = json.dumps(data, sort_keys=True)
                data_hash = hashlib.sha256(data_str.encode()).hexdigest()
                
                # 检查是否已存在
                if RawCrawl.objects.filter(hash=data_hash).exists():
                    continue
                
                # 保存原始数据
                RawCrawl.objects.create(
                    source=source,
                    payload=data,
                    hash=data_hash
                )
                
                # 解析并更新游戏数据
                self._update_game_from_crawl(source, data)
                
                processed_count += 1
                
            except Exception as e:
                logger.error(f"Error processing crawled data: {e}", exc_info=True)
        
        logger.info(f"Processed {processed_count} items from {source}")
        return processed_count
    
    def _update_game_from_crawl(self, source, data):
        """
        从爬取数据更新游戏信息
        """
        try:
            # 根据不同数据源解析数据（示例）
            game_name = data.get('name') or data.get('title')
            if not game_name:
                return
            
            # 查找或创建发行商
            publisher_name = data.get('publisher', 'Unknown')
            publisher, _ = Publisher.objects.get_or_create(
                name=publisher_name,
                defaults={'contact_info': ''}
            )
            
            # 查找或创建游戏
            game, created = Game.objects.get_or_create(
                name=game_name,
                publisher=publisher,
                defaults={
                    'category': data.get('category', 'Unknown'),
                    'rating': data.get('rating', 0.0),
                    'description': data.get('description', ''),
                }
            )
            
            # 更新统计数据
            if not created:
                if 'rating' in data:
                    game.rating = data['rating']
                if 'download_count' in data:
                    game.download_count = data['download_count']
                game.save()
            
            # 处理标签
            if 'tags' in data and isinstance(data['tags'], list):
                for tag_name in data['tags']:
                    tag, _ = Tag.objects.get_or_create(name=tag_name)
                    game.tags.add(tag)
            
            logger.debug(f"Updated game {game_name} from {source}")
            
        except Exception as e:
            logger.error(f"Error updating game from crawl data: {e}")
    
    def calculate_daily_metrics(self, date=None):
        """
        计算每日游戏指标
        """
        if date is None:
            date = timezone.now().date()
        
        games = Game.objects.all()
        metrics_list = []
        
        for game in games:
            try:
                # 统计当日数据
                metrics = self._calculate_game_metrics(game, date)
                
                # 创建或更新每日指标
                daily_metric, created = GameMetricsDaily.objects.update_or_create(
                    game=game,
                    date=date,
                    defaults=metrics
                )
                
                metrics_list.append(daily_metric)
                
            except Exception as e:
                logger.error(f"Error calculating metrics for game {game.id}: {e}")
        
        logger.info(f"Calculated daily metrics for {len(metrics_list)} games on {date}")
        return metrics_list
    
    def _calculate_game_metrics(self, game, date):
        """
        计算单个游戏的指标
        """
        from apps.recommendations.services import recommendation_service
        
        # 计算热度
        heat_static, heat_dynamic, heat_total = recommendation_service.calculate_total_heat(game)
        
        # 统计当日帖子和互动
        start_date = datetime.combine(date, datetime.min.time())
        end_date = datetime.combine(date, datetime.max.time())
        
        posts_count = Post.objects.filter(
            game=game,
            created_at__range=(start_date, end_date)
        ).count()
        
        likes_count = Post.objects.filter(
            game=game,
            created_at__range=(start_date, end_date)
        ).aggregate(total=Sum('like_count'))['total'] or 0
        
        comments_count = Comment.objects.filter(
            game=game,
            created_at__range=(start_date, end_date)
        ).count()
        
        return {
            'downloads': game.download_count,
            'follows': game.follow_count,
            'reviews': game.review_count,
            'posts': posts_count,
            'likes': likes_count,
            'comments': comments_count,
            'heat_static': heat_static,
            'heat_dynamic': heat_dynamic,
            'heat_total': heat_total,
        }
    
    def generate_overview_data(self, days=30):
        """
        生成概览趋势数据（供 ECharts 使用）
        """
        cache_key = f"overview_trend:{days}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        # 查询每日指标
        daily_metrics = GameMetricsDaily.objects.filter(
            date__range=(start_date, end_date)
        ).values('date').annotate(
            total_downloads=Sum('downloads'),
            total_follows=Sum('follows'),
            total_reviews=Sum('reviews'),
            avg_heat=Avg('heat_total')
        ).order_by('date')
        
        # 转换为 ECharts 格式
        dates = []
        downloads = []
        follows = []
        reviews = []
        heat = []
        
        for metric in daily_metrics:
            dates.append(metric['date'].strftime('%Y-%m-%d'))
            downloads.append(metric['total_downloads'] or 0)
            follows.append(metric['total_follows'] or 0)
            reviews.append(metric['total_reviews'] or 0)
            heat.append(round(metric['avg_heat'] or 0, 2))
        
        data = {
            'dates': dates,
            'series': [
                {'name': '下载数', 'data': downloads},
                {'name': '关注数', 'data': follows},
                {'name': '评价数', 'data': reviews},
                {'name': '平均热度', 'data': heat},
            ]
        }
        
        # 缓存1小时
        cache.set(cache_key, data, 3600)
        
        # 保存到仪表盘缓存
        DashCardCache.objects.update_or_create(
            key='overview_trend',
            defaults={
                'snapshot': data,
                'description': f'最近{days}天概览趋势'
            }
        )
        
        return data
    
    def generate_heatmap_data(self):
        """
        生成热度分布热力图数据
        """
        cache_key = "heatmap_category"
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        
        # 按类别统计游戏热度
        category_stats = Game.objects.values('category').annotate(
            count=Count('id'),
            avg_heat=Avg('heat_total'),
            total_heat=Sum('heat_total')
        ).order_by('-total_heat')[:20]
        
        categories = []
        heat_values = []
        
        for stat in category_stats:
            categories.append(stat['category'])
            heat_values.append(round(stat['avg_heat'] or 0, 2))
        
        data = {
            'categories': categories,
            'values': heat_values
        }
        
        # 缓存1小时
        cache.set(cache_key, data, 3600)
        
        # 保存到仪表盘缓存
        DashCardCache.objects.update_or_create(
            key='heatmap_category',
            defaults={
                'snapshot': data,
                'description': '各类别游戏热度分布'
            }
        )
        
        return data
    
    def generate_publisher_stats(self, publisher_id):
        """
        生成发行商统计数据
        """
        cache_key = f"publisher_stats:{publisher_id}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            publisher = Publisher.objects.get(id=publisher_id)
        except Publisher.DoesNotExist:
            return None
        
        # 统计发行商的游戏
        games = publisher.games.all()
        
        # 总体统计
        total_stats = games.aggregate(
            total_games=Count('id'),
            total_downloads=Sum('download_count'),
            total_follows=Sum('follow_count'),
            avg_rating=Avg('rating'),
            avg_heat=Avg('heat_total')
        )
        
        # 各游戏的曝光和评价
        game_stats = []
        for game in games[:10]:  # 只取前10个游戏
            game_stats.append({
                'name': game.name,
                'downloads': game.download_count,
                'follows': game.follow_count,
                'rating': round(game.rating, 1),
                'heat': round(game.heat_total, 2)
            })
        
        data = {
            'publisher': {
                'id': publisher.id,
                'name': publisher.name
            },
            'summary': {
                'total_games': total_stats['total_games'],
                'total_downloads': total_stats['total_downloads'] or 0,
                'total_follows': total_stats['total_follows'] or 0,
                'avg_rating': round(total_stats['avg_rating'] or 0, 2),
                'avg_heat': round(total_stats['avg_heat'] or 0, 2)
            },
            'games': game_stats
        }
        
        # 缓存30分钟
        cache.set(cache_key, data, 1800)
        
        return data
    
    def clean_old_data(self, days=90):
        """
        清理旧数据
        """
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # 清理旧的爬取数据
        deleted_crawl = RawCrawl.objects.filter(created_at__lt=cutoff_date).delete()
        
        # 清理旧的每日指标（保留更长时间）
        metrics_cutoff = timezone.now().date() - timedelta(days=365)
        deleted_metrics = GameMetricsDaily.objects.filter(date__lt=metrics_cutoff).delete()
        
        logger.info(f"Cleaned old data: {deleted_crawl[0]} crawl records, {deleted_metrics[0]} daily metrics")
        
        return {
            'crawl_records': deleted_crawl[0],
            'daily_metrics': deleted_metrics[0]
        }


# 全局服务实例
analytics_service = AnalyticsService()

