"""
Analytics Celery tasks
"""
from celery import shared_task
from .services import analytics_service
from apps.recommendations.services import recommendation_service
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def crawl_external_data(self):
    """
    爬取外部数据任务
    每日凌晨2点执行
    """
    try:
        from scripts.crawl_run import run_all_crawlers
        
        logger.info("Starting crawl task...")
        results = run_all_crawlers()
        logger.info(f"Crawl task completed: {results}")
        
        return results
    except Exception as e:
        logger.error(f"Crawl task failed: {e}", exc_info=True)
        raise self.retry(exc=e, countdown=300)  # 5分钟后重试


@shared_task(bind=True)
def calculate_game_heat(self):
    """
    计算游戏热度任务
    每日凌晨3点执行
    """
    try:
        logger.info("Starting heat calculation task...")
        
        # 更新所有游戏的热度
        count = recommendation_service.update_all_games_heat()
        
        # 计算每日指标
        metrics = analytics_service.calculate_daily_metrics()
        
        logger.info(f"Heat calculation completed: {count} games, {len(metrics)} metrics")
        
        return {
            'games_updated': count,
            'metrics_created': len(metrics)
        }
    except Exception as e:
        logger.error(f"Heat calculation task failed: {e}", exc_info=True)
        raise


@shared_task(bind=True)
def generate_dashboard_data(self):
    """
    生成仪表盘数据任务
    """
    try:
        logger.info("Generating dashboard data...")
        
        # 生成概览数据
        overview = analytics_service.generate_overview_data()
        
        # 生成热力图数据
        heatmap = analytics_service.generate_heatmap_data()
        
        logger.info("Dashboard data generation completed")
        
        return {
            'overview': len(overview.get('dates', [])),
            'heatmap': len(heatmap.get('categories', []))
        }
    except Exception as e:
        logger.error(f"Dashboard data generation failed: {e}", exc_info=True)
        raise


@shared_task(bind=True)
def clean_old_analytics_data(self):
    """
    清理旧的分析数据
    每周执行一次
    """
    try:
        logger.info("Cleaning old analytics data...")
        
        result = analytics_service.clean_old_data(days=90)
        
        logger.info(f"Cleanup completed: {result}")
        
        return result
    except Exception as e:
        logger.error(f"Cleanup task failed: {e}", exc_info=True)
        raise

