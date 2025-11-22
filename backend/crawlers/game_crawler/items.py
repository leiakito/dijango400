"""
Scrapy items
"""
import scrapy


class GameItem(scrapy.Item):
    """游戏数据项"""
    name = scrapy.Field()
    category = scrapy.Field()
    publisher = scrapy.Field()
    rating = scrapy.Field()
    download_count = scrapy.Field()
    description = scrapy.Field()
    tags = scrapy.Field()
    release_date = scrapy.Field()
    source = scrapy.Field()

