"""
Games Views - 游戏管理模块视图
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, SAFE_METHODS
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Game, Publisher, Tag, Collection, SinglePlayerRanking, GameScreenshot
from .serializers import (
    GameListSerializer, GameDetailSerializer, GameCreateSerializer,
    PublisherSerializer, TagSerializer,
    CollectionSerializer, SinglePlayerRankingSerializer,
    GameScreenshotSerializer, GameScreenshotCreateSerializer
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

    @action(detail=True, methods=['post'], permission_classes=[IsAdminOrPublisher])
    def upload_screenshot(self, request, pk=None):
        """上传游戏截图"""
        game = self.get_object()
        
        # 检查权限
        if not (request.user.is_staff or game.publisher.id == request.user.id):
            return Response(
                {'error': '您没有权限上传此游戏的截图'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if 'image' not in request.FILES:
            return Response(
                {'error': '请提供图片文件'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 获取排序号
        order = request.data.get('order', 0)
        title = request.data.get('title', '')
        description = request.data.get('description', '')
        
        try:
            order = int(order)
        except (ValueError, TypeError):
            order = 0
        
        # 创建截图
        screenshot = GameScreenshot.objects.create(
            game=game,
            image=request.FILES['image'],
            title=title,
            description=description,
            order=order
        )
        
        serializer = GameScreenshotSerializer(screenshot, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


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


class GameScreenshotViewSet(viewsets.ModelViewSet):
    """
    游戏截图视图集
    """
    queryset = GameScreenshot.objects.all()
    serializer_class = GameScreenshotSerializer
    permission_classes = [AllowAny]
    
    def get_permissions(self):
        """
        列表和详情为公开，创建/更新/删除需要权限
        """
        if self.request.method in SAFE_METHODS:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminOrPublisher]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        """根据操作返回不同的序列化器"""
        if self.action in ['create', 'update', 'partial_update']:
            return GameScreenshotCreateSerializer
        return GameScreenshotSerializer
    
    def get_queryset(self):
        """按游戏和排序号过滤"""
        qs = super().get_queryset()
        game_id = self.request.query_params.get('game_id')
        if game_id:
            qs = qs.filter(game_id=game_id)
        return qs.order_by('game', 'order', '-created_at')
    
    def perform_create(self, serializer):
        """创建时检查权限"""
        game = serializer.validated_data.get('game')
        if game and not (self.request.user.is_staff or game.publisher.id == self.request.user.id):
            return Response(
                {'error': '您没有权限上传此游戏的截图'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save()
    
    def perform_update(self, serializer):
        """更新时检查权限"""
        screenshot = self.get_object()
        if not (self.request.user.is_staff or screenshot.game.publisher.id == self.request.user.id):
            return Response(
                {'error': '您没有权限修改此截图'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save()
    
    def perform_destroy(self, instance):
        """删除时检查权限"""
        if not (self.request.user.is_staff or instance.game.publisher.id == self.request.user.id):
            return Response(
                {'error': '您没有权限删除此截图'},
                status=status.HTTP_403_FORBIDDEN
            )
        instance.delete()
