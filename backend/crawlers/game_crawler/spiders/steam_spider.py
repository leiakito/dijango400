"""
Steam 游戏爬虫示例
注意：这是一个示例爬虫，实际使用时需要根据目标网站的结构调整
"""
import scrapy
from ..items import GameItem


class SteamSpider(scrapy.Spider):
    name = 'steam'
    allowed_domains = ['store.steampowered.com']
    
    # 示例起始URL（实际使用时需要调整）
    start_urls = [
        'https://store.steampowered.com/search/?filter=topsellers'
    ]
    
    def parse(self, response):
        """
        解析游戏列表页面
        注意：这是示例代码，实际选择器需要根据网站结构调整
        """
        # 示例：提取游戏链接
        game_links = response.css('a.search_result_row::attr(href)').getall()
        
        for link in game_links[:10]:  # 限制数量用于测试
            yield scrapy.Request(link, callback=self.parse_game)
    
    def parse_game(self, response):
        """
        解析单个游戏详情页面
        注意：这是示例代码，实际选择器需要根据网站结构调整
        """
        item = GameItem()
        
        # 示例：提取游戏信息（需要根据实际页面结构调整）
        item['name'] = response.css('div.apphub_AppName::text').get()
        item['category'] = 'Action'  # 示例分类
        item['publisher'] = response.css('div.dev_row a::text').get()
        item['description'] = response.css('div.game_description_snippet::text').get()
        item['tags'] = response.css('a.app_tag::text').getall()
        item['rating'] = 0.0  # 需要从页面提取
        item['download_count'] = 0  # Steam 不公开下载数
        item['release_date'] = response.css('div.release_date div.date::text').get()
        item['source'] = 'steam'
        
        yield item

