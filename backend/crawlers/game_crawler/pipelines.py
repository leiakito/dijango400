"""
Scrapy pipelines
"""
import os
import sys
import django

# 设置 Django 环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from apps.analytics.services import analytics_service
from apps.analytics.models import CrawlJob


class GameCrawlerPipeline:
    """游戏爬虫数据处理管道"""
    
    def __init__(self):
        self.items = []
        self.crawl_job = None
    
    def open_spider(self, spider):
        """爬虫开始时创建任务记录"""
        self.crawl_job = CrawlJob.objects.create(
            source=spider.name,
            status=CrawlJob.Status.RUNNING
        )
        spider.logger.info(f"Created crawl job {self.crawl_job.id}")
    
    def close_spider(self, spider):
        """爬虫结束时处理数据"""
        try:
            # 处理收集的数据
            if self.items:
                count = analytics_service.process_crawled_data(
                    source=spider.name,
                    data_list=self.items
                )
                
                self.crawl_job.items_count = count
                self.crawl_job.status = CrawlJob.Status.SUCCESS
            else:
                self.crawl_job.status = CrawlJob.Status.SUCCESS
                self.crawl_job.items_count = 0
            
            spider.logger.info(f"Processed {len(self.items)} items")
        
        except Exception as e:
            self.crawl_job.status = CrawlJob.Status.FAILED
            self.crawl_job.error_message = str(e)
            spider.logger.error(f"Pipeline error: {e}")
        
        finally:
            from django.utils import timezone
            self.crawl_job.finished_at = timezone.now()
            self.crawl_job.save()
    
    def process_item(self, item, spider):
        """处理单个数据项"""
        # 转换为字典并添加到列表
        self.items.append(dict(item))
        return item

