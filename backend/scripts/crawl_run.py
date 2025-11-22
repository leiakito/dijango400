"""
爬虫运行脚本
"""
import os
import sys
import django
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# 设置 Django 环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()


def run_all_crawlers():
    """
    运行所有爬虫
    """
    from crawlers.game_crawler.spiders.steam_spider import SteamSpider
    
    # 获取 Scrapy 设置
    settings = get_project_settings()
    settings.set('SPIDER_MODULES', ['crawlers.game_crawler.spiders'])
    
    # 创建爬虫进程
    process = CrawlerProcess(settings)
    
    # 添加爬虫
    process.crawl(SteamSpider)
    # 可以添加更多爬虫
    # process.crawl(EpicSpider)
    # process.crawl(GOGSpider)
    
    # 启动爬虫
    process.start()
    
    return {'status': 'completed'}


def run_spider(spider_name):
    """
    运行指定的爬虫
    """
    from crawlers.game_crawler.spiders.steam_spider import SteamSpider
    
    spiders = {
        'steam': SteamSpider,
    }
    
    if spider_name not in spiders:
        raise ValueError(f"Unknown spider: {spider_name}")
    
    settings = get_project_settings()
    settings.set('SPIDER_MODULES', ['crawlers.game_crawler.spiders'])
    
    process = CrawlerProcess(settings)
    process.crawl(spiders[spider_name])
    process.start()
    
    return {'status': 'completed', 'spider': spider_name}


if __name__ == '__main__':
    if len(sys.argv) > 1:
        spider_name = sys.argv[1]
        print(f"Running spider: {spider_name}")
        run_spider(spider_name)
    else:
        print("Running all spiders...")
        run_all_crawlers()

