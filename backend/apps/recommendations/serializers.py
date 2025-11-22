"""
Recommendation serializers
"""
from rest_framework import serializers
from .models import AlgoConfig, Recommendation, GameMetricsDaily, UserInterest
from apps.games.serializers import GameListSerializer


class AlgoConfigSerializer(serializers.ModelSerializer):
    """
    算法配置序列化器
    """
    class Meta:
        model = AlgoConfig
        fields = [
            'id', 'alpha', 'beta', 'decay_lambda',
            'weight_download', 'weight_follow', 'weight_review',
            'weight_like', 'weight_comment', 'top_k', 
            'refresh_hours', 'updated_at'
        ]
        read_only_fields = ['id', 'updated_at']


class RecommendationSerializer(serializers.ModelSerializer):
    """
    推荐记录序列化器
    """
    game = GameListSerializer(read_only=True)
    
    class Meta:
        model = Recommendation
        fields = ['id', 'user', 'game', 'reason', 'score', 'generated_at']
        read_only_fields = ['id', 'generated_at']


class GameMetricsDailySerializer(serializers.ModelSerializer):
    """
    游戏每日指标序列化器
    """
    game_name = serializers.CharField(source='game.name', read_only=True)
    
    class Meta:
        model = GameMetricsDaily
        fields = [
            'id', 'game', 'game_name', 'date',
            'downloads', 'follows', 'reviews', 'posts', 'likes', 'comments',
            'heat_static', 'heat_dynamic', 'heat_total', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class UserInterestSerializer(serializers.ModelSerializer):
    """
    用户兴趣序列化器
    """
    tag_name = serializers.CharField(source='tag.name', read_only=True)
    
    class Meta:
        model = UserInterest
        fields = ['id', 'user', 'tag', 'tag_name', 'weight', 'updated_at']
        read_only_fields = ['id', 'updated_at']

