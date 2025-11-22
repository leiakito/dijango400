"""
Games Views - 游戏管理模块视图
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, SAFE_METHODS
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Game, Publisher, Tag, Collection, SinglePlayerRanking
from .serializers import (
    GameListSerializer, GameDetailSerializer, GameCreateSerializer,
    PublisherSerializer, TagSerializer,
    CollectionSerializer, SinglePlayerRankingSerializer
)
from .filters import GameFilter
from config.permissions import IsAdminOrPublisher


class GameViewSet(viewsets.ModelViewSet):
    """
    游戏视图集（提供公开读取，发行商/管理员可维护）
    """
    queryset = Game.objects.all()
    permission_classes = [AllowAny]  # 公开访问
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = GameFilter
    search_fields = ['name', 'description']
    ordering_fields = ['release_date', 'rating', 'download_count', 'heat_total', 'created_at']
    ordering = ['-heat_total']
    http_method_names = ['get', 'post', 'patch', 'head', 'options']

    def get_permissions(self):
        """
        公共读取接口保持开放，其余写操作限制为发行商或管理员。
        收藏操作需要登录即可。
        """
        if self.action == 'collect':
            permission_classes = [IsAuthenticated]
        elif self.request.method in SAFE_METHODS:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminOrPublisher]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        """根据操作返回不同的序列化器"""
        if self.action == 'list':
            return GameListSerializer
        if self.action == 'create':
            return GameCreateSerializer
        return GameDetailSerializer

    @action(detail=True, methods=['post'])
    def collect(self, request, pk=None):
        """收藏/取消收藏游戏"""
        game = self.get_object()
        user = request.user
        
        if not user.is_authenticated:
            return Response(
                {'error': '请先登录'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        collection, created = Collection.objects.get_or_create(
            user=user,
            game=game
        )
        
        if not created:
            # 已经收藏，执行取消收藏
            collection.delete()
            game.follow_count = max(0, game.follow_count - 1)
            game.save(update_fields=['follow_count'])
            is_collected = False
            message = '取消收藏成功'
        else:
            # 新收藏
            game.follow_count += 1
            game.save(update_fields=['follow_count'])
            is_collected = True
            message = '收藏成功'
        
        # 清除用户的推荐缓存，以便下次获取时重新计算
        from apps.recommendations.services import recommendation_service
        recommendation_service.clear_user_recommendations_cache(user)
        
        return Response({'message': message, 'is_collected': is_collected})


class PublisherViewSet(viewsets.ReadOnlyModelViewSet):
    """
    发行商视图集（只读）
    """
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer
    permission_classes = [AllowAny]
    search_fields = ['name']
    ordering = ['name']


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    标签视图集（只读）
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    search_fields = ['name']
    ordering = ['name']


class SinglePlayerRankingViewSet(viewsets.ReadOnlyModelViewSet):
    """
    单机游戏排行榜视图（只读）
    """
    queryset = SinglePlayerRanking.objects.all().order_by('rank')
    serializer_class = SinglePlayerRankingSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        qs = super().get_queryset()
        source = self.request.query_params.get('source', '3dm')
        limit = self.request.query_params.get('limit')

        if source:
            qs = qs.filter(source=source)
        if limit and str(limit).isdigit():
            qs = qs[: int(limit)]
        return qs
