"""
Analytics serializers
"""
from rest_framework import serializers
from .models import RawCrawl, DashCardCache, CrawlJob


class RawCrawlSerializer(serializers.ModelSerializer):
    """
    原始爬取数据序列化器
    """
    class Meta:
        model = RawCrawl
        fields = ['id', 'source', 'payload', 'hash', 'created_at']
        read_only_fields = ['id', 'created_at']


class DashCardCacheSerializer(serializers.ModelSerializer):
    """
    仪表盘缓存序列化器
    """
    class Meta:
        model = DashCardCache
        fields = ['id', 'key', 'snapshot', 'description', 'updated_at']
        read_only_fields = ['id', 'updated_at']


class CrawlJobSerializer(serializers.ModelSerializer):
    """
    爬虫任务序列化器
    """
    duration = serializers.SerializerMethodField()
    
    class Meta:
        model = CrawlJob
        fields = [
            'id', 'source', 'status', 'items_count', 
            'error_message', 'started_at', 'finished_at', 'duration'
        ]
        read_only_fields = ['id', 'started_at']
    
    def get_duration(self, obj):
        return obj.duration

