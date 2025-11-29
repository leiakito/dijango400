"""
Game serializers
"""
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
import random

from apps.community.models import Reaction
from .models import Publisher, Tag, Game, GameScreenshot, Collection, SinglePlayerRanking


class GameLikeMixin:
    """
    公共方法：判断当前用户是否点赞了某个游戏
    """
    _game_content_type = None

    def _get_game_content_type(self):
        if self._game_content_type is None:
            self._game_content_type = ContentType.objects.get_for_model(Game)
        return self._game_content_type

    def _is_liked_by_user(self, user, game_obj: Game) -> bool:
        if not user or not user.is_authenticated:
            return False
        return Reaction.objects.filter(
            user=user,
            content_type=self._get_game_content_type(),
            object_id=game_obj.id,
            type=Reaction.ReactionType.LIKE
        ).exists()


class TagSerializer(serializers.ModelSerializer):
    """
    标签序列化器
    """
    class Meta:
        model = Tag
        fields = ['id', 'name', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']


class PublisherSerializer(serializers.ModelSerializer):
    """
    发行商序列化器
    """
    games_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Publisher
        fields = [
            'id', 'name', 'contact_info', 'logo', 'description', 
            'website', 'games_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_games_count(self, obj):
        return obj.games.count()


class GameListSerializer(GameLikeMixin, serializers.ModelSerializer):
    """
    游戏列表序列化器（简化版）
    """
    publisher_name = serializers.CharField(source='publisher.name', read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    cover_image = serializers.SerializerMethodField()
    is_collected = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Game
        fields = [
            'id', 'name', 'category', 'publisher', 'publisher_name',
            'tags', 'rating', 'download_count', 'follow_count', 
            'like_count', 'review_count', 'cover_image', 'heat_total', 'release_date',
            'is_collected', 'is_liked'
        ]
        read_only_fields = ['id', 'heat_total', 'is_collected', 'is_liked']
    
    def get_cover_image(self, obj):
        """返回完整的图片URL"""
        # 优先使用本地存储的封面（支持直接存储远程 URL 字符串）
        if obj.cover_image:
            cover_str = str(obj.cover_image)
            if cover_str.startswith('http://') or cover_str.startswith('https://'):
                return cover_str
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.cover_image.url)
            return obj.cover_image.url

        # 退化到排行榜抓取的封面
        ranking = obj.rankings.order_by('rank').first()
        if ranking and ranking.cover_url:
            return ranking.cover_url
        return None
    
    def get_is_collected(self, obj):
        """判断当前用户是否收藏了该游戏"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Collection.objects.filter(user=request.user, game=obj).exists()
        return False

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request:
            return self._is_liked_by_user(request.user, obj)
        return False


class GameScreenshotSerializer(serializers.ModelSerializer):
    """
    游戏截图序列化器
    """
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = GameScreenshot
        fields = ['id', 'image', 'image_url', 'title', 'description', 'order', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_image_url(self, obj):
        """返回完整的图片URL"""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class GameScreenshotCreateSerializer(serializers.ModelSerializer):
    """
    游戏截图创建序列化器
    """
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = GameScreenshot
        fields = ['id', 'game', 'image', 'image_url', 'title', 'description', 'order', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_image_url(self, obj):
        """返回完整的图片URL"""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class GameDetailSerializer(GameLikeMixin, serializers.ModelSerializer):
    """
    游戏详情序列化器
    """
    publisher = PublisherSerializer(read_only=True)
    publisher_id = serializers.PrimaryKeyRelatedField(
        queryset=Publisher.objects.all(),
        source='publisher',
        write_only=True
    )
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        source='tags',
        write_only=True,
        required=False
    )
    cover_image = serializers.SerializerMethodField()
    screenshots = GameScreenshotSerializer(many=True, read_only=True)
    is_collected = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Game
        fields = [
            'id', 'name', 'category', 'publisher', 'publisher_id',
            'tags', 'tag_ids', 'rating', 'download_count', 
            'follow_count', 'review_count', 'release_date', 
            'online_time', 'version', 'description', 'cover_image', 'screenshots',
            'heat_static', 'heat_dynamic', 'heat_total', 'like_count',
            'is_collected', 'is_liked', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'rating', 'download_count', 'follow_count', 
            'review_count', 'heat_static', 'heat_dynamic', 'heat_total',
            'like_count', 'is_collected', 'is_liked', 'created_at', 'updated_at'
        ]
    
    def get_cover_image(self, obj):
        """返回完整的图片URL"""
        if obj.cover_image:
            cover_str = str(obj.cover_image)
            if cover_str.startswith('http://') or cover_str.startswith('https://'):
                return cover_str
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.cover_image.url)
            return obj.cover_image.url

        ranking = obj.rankings.order_by('rank').first()
        if ranking and ranking.cover_url:
            return ranking.cover_url
        return None
    
    def get_is_collected(self, obj):
        """判断当前用户是否收藏了该游戏"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Collection.objects.filter(user=request.user, game=obj).exists()
        return False

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request:
            return self._is_liked_by_user(request.user, obj)
        return False


class GameCreateSerializer(serializers.ModelSerializer):
    """
    游戏创建序列化器（发行商使用）
    """
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        source='tags',
        required=False
    )
    screenshots = GameScreenshotSerializer(many=True, read_only=True)
    
    class Meta:
        model = Game
        fields = [
            'id', 'name', 'category', 'publisher', 'tag_ids',
            'release_date', 'online_time', 'version', 
            'description', 'cover_image', 'screenshots', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'screenshots', 'created_at', 'updated_at']

    def create(self, validated_data):
        """创建游戏时，若未提供评分则随机生成一个评分（保留 1 位小数）。"""
        tags = validated_data.pop('tags', [])
        game = Game.objects.create(**validated_data)
        if tags:
            game.tags.set(tags)

        updated_fields = []

        # 随机评分（6.0 ~ 9.6），仅当未提供或为 0 时
        if not game.rating or float(game.rating) == 0.0:
            game.rating = round(random.uniform(6.0, 9.6), 1)
            updated_fields.append('rating')

        # 随机基础统计，仅当为 0 时
        if not game.download_count:
            game.download_count = random.randint(500, 50000)
            updated_fields.append('download_count')
        if not game.follow_count:
            game.follow_count = random.randint(50, 8000)
            updated_fields.append('follow_count')
        if not game.review_count:
            game.review_count = random.randint(0, 2000)
            updated_fields.append('review_count')

        # 初始化热度（使用静态热度近似总热度），仅当当前为 0 时
        if not game.heat_static:
            heat_static = 0.5 * game.download_count + 0.3 * game.follow_count + 0.2 * game.review_count
            game.heat_static = float(heat_static)
            game.heat_dynamic = 0.0
            game.heat_total = float(heat_static)
            updated_fields += ['heat_static', 'heat_dynamic', 'heat_total']

        if updated_fields:
            game.save(update_fields=list(set(updated_fields)))
        return game


class CollectionSerializer(serializers.ModelSerializer):
    """
    收藏序列化器
    """
    game = GameListSerializer(read_only=True)
    game_id = serializers.PrimaryKeyRelatedField(
        queryset=Game.objects.all(),
        source='game',
        write_only=True
    )
    
    class Meta:
        model = Collection
        fields = ['id', 'user', 'game', 'game_id', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class SinglePlayerRankingSerializer(serializers.ModelSerializer):
    """
    单机游戏排行榜序列化器
    """
    class Meta:
        model = SinglePlayerRanking
        fields = [
            'id', 'source', 'rank', 'name', 'english_name', 'developer',
            'publisher_name', 'genre', 'platforms', 'language', 'release_date',
            'score', 'rating_count', 'tags', 'cover_url', 'detail_url',
            'game', 'fetched_at'
        ]
        read_only_fields = fields
