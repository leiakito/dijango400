"""
Content serializers
"""
from rest_framework import serializers
from .models import Strategy, MediaAsset, ContentReview, StrategyCollection, StrategyLike, StrategyComment, Incentive
from apps.users.serializers import UserProfileSerializer, CurrentUserSerializer
from apps.games.serializers import GameListSerializer


class MediaAssetSerializer(serializers.ModelSerializer):
    """
    媒体资源序列化器
    """
    url = serializers.SerializerMethodField(read_only=True)
    file = serializers.FileField(write_only=True, required=True, source='url')
    
    class Meta:
        model = MediaAsset
        fields = ['id', 'strategy', 'type', 'url', 'file', 'meta', 'order', 'created_at']
        read_only_fields = ['id', 'created_at', 'url']
        extra_kwargs = {
            'strategy': {'write_only': True, 'required': False},
            'type': {'required': False},
        }

    def get_url(self, obj):
        """返回完整 URL（支持远程 URL 字符串）"""
        if not obj.url:
            return None
        url_str = str(obj.url)
        if url_str.startswith('http://') or url_str.startswith('https://'):
            return url_str
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.url.url)
        return obj.url.url


class ContentReviewSerializer(serializers.ModelSerializer):
    """
    内容审核序列化器
    """
    reviewer_name = serializers.CharField(source='reviewer.username', read_only=True)
    
    class Meta:
        model = ContentReview
        fields = [
            'id', 'strategy', 'auto_hit_keywords', 'reviewer', 
            'reviewer_name', 'decision', 'reason', 'reviewed_at'
        ]
        read_only_fields = ['id', 'reviewed_at']


class StrategyListSerializer(serializers.ModelSerializer):
    """
    攻略列表序列化器
    """
    author = UserProfileSerializer(read_only=True)
    game = GameListSerializer(read_only=True)
    media_count = serializers.SerializerMethodField()
    is_collected = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Strategy
        fields = [
            'id', 'title', 'author', 'game', 'status',
            'view_count', 'like_count', 'collect_count',
            'comment_count',
            'media_count', 'publish_date', 'created_at',
            'is_collected', 'is_liked'
        ]
        read_only_fields = ['id', 'view_count', 'like_count', 'collect_count', 'comment_count', 'created_at']
    
    def get_media_count(self, obj):
        return obj.media_assets.count()
    
    def get_is_collected(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return StrategyCollection.objects.filter(user=request.user, strategy=obj).exists()
        return False
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return StrategyLike.objects.filter(user=request.user, strategy=obj).exists()
        return False


class StrategyDetailSerializer(serializers.ModelSerializer):
    """
    攻略详情序列化器
    """
    author = UserProfileSerializer(read_only=True)
    game = GameListSerializer(read_only=True)
    game_id = serializers.PrimaryKeyRelatedField(
        queryset=__import__('apps.games.models', fromlist=['Game']).Game.objects.all(),
        source='game',
        write_only=True
    )
    media_assets = MediaAssetSerializer(many=True, read_only=True)
    reviews = ContentReviewSerializer(many=True, read_only=True)
    is_collected = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Strategy
        fields = [
            'id', 'title', 'content', 'author', 'game', 'game_id',
            'status', 'view_count', 'like_count', 'collect_count', 'comment_count',
            'media_assets', 'reviews', 'publish_date',
            'is_collected', 'is_liked',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'author', 'status', 'view_count', 'like_count', 
            'collect_count', 'comment_count', 'publish_date', 'created_at', 'updated_at'
        ]

    def get_is_collected(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return StrategyCollection.objects.filter(user=request.user, strategy=obj).exists()
        return False

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return StrategyLike.objects.filter(user=request.user, strategy=obj).exists()
        return False


class StrategyCommentSerializer(serializers.ModelSerializer):
    """
    攻略评论序列化
    """
    user = CurrentUserSerializer(read_only=True)

    class Meta:
        model = StrategyComment
        fields = ['id', 'strategy', 'user', 'content', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
        extra_kwargs = {
            'strategy': {'write_only': True}
        }


class IncentiveSerializer(serializers.ModelSerializer):
    """
    创作者激励记录序列化
    """
    author = CurrentUserSerializer(read_only=True)

    class Meta:
        model = Incentive
        fields = [
            'id', 'author', 'period', 'exposure', 'likes', 'comments',
            'publish_count', 'status', 'reason', 'reward_amount',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']


class StrategyCreateSerializer(serializers.ModelSerializer):
    """
    攻略创建序列化器
    """
    class Meta:
        model = Strategy
        fields = ['id', 'title', 'content', 'game']
        read_only_fields = ['id']


class StrategyCollectionSerializer(serializers.ModelSerializer):
    """
    攻略收藏序列化器
    """
    strategy = StrategyListSerializer(read_only=True)
    strategy_id = serializers.PrimaryKeyRelatedField(
        queryset=Strategy.objects.all(),
        source='strategy',
        write_only=True
    )
    
    class Meta:
        model = StrategyCollection
        fields = ['id', 'user', 'strategy', 'strategy_id', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
