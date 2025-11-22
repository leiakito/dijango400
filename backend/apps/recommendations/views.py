"""
Recommendation views
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import AlgoConfig, Recommendation, GameMetricsDaily
from .serializers import (
    AlgoConfigSerializer, RecommendationSerializer, GameMetricsDailySerializer
)
from .services import recommendation_service
from config.permissions import IsAdmin


class AlgoConfigViewSet(viewsets.ModelViewSet):
    """
    算法配置视图集
    """
    queryset = AlgoConfig.objects.all()
    serializer_class = AlgoConfigSerializer
    permission_classes = [IsAdmin]
    
    def get_object(self):
        """获取单例配置"""
        return AlgoConfig.get_config()
    
    def list(self, request):
        """获取配置"""
        config = self.get_object()
        serializer = self.get_serializer(config)
        return Response(serializer.data)
    
    def update(self, request, pk=None):
        """更新配置"""
        config = self.get_object()
        serializer = self.get_serializer(config, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([])  # 允许匿名访问
def hot_games(request):
    """
    热门游戏榜单（公开接口）
    GET /api/v1/recommend/hot/?category=&top=10
    """
    category = request.query_params.get('category')
    top_k = int(request.query_params.get('top', 10))
    
    games = recommendation_service.get_hot_games(category=category, top_k=top_k)
    
    from apps.games.serializers import GameListSerializer
    # 传递 request 上下文，确保图片 URL 正确生成
    serializer = GameListSerializer(games, many=True, context={'request': request})
    
    return Response({
        'category': category or 'all',
        'count': len(games),
        'results': serializer.data
    })


@api_view(['GET'])
@permission_classes([])  # 允许匿名访问
def new_games(request):
    """
    最新游戏榜单（公开接口）
    GET /api/v1/recommend/new/?category=&top=10
    """
    category = request.query_params.get('category')
    top_k = int(request.query_params.get('top', 10))
    
    games = recommendation_service.get_new_games(category=category, top_k=top_k)
    
    from apps.games.serializers import GameListSerializer
    # 传递 request 上下文，确保图片 URL 正确生成
    serializer = GameListSerializer(games, many=True, context={'request': request})
    
    return Response({
        'category': category or 'all',
        'count': len(games),
        'results': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def personal_recommendations(request):
    """
    个性化推荐（猜你喜欢）
    GET /api/v1/recommend/personal/?top=10
    """
    top_k = int(request.query_params.get('top', 10))
    user = request.user
    
    recommendations = recommendation_service.get_personal_recommendations(user, top_k=top_k)
    # 传递 request 上下文，确保图片 URL 正确生成
    serializer = RecommendationSerializer(recommendations, many=True, context={'request': request})
    
    return Response({
        'count': len(recommendations),
        'results': serializer.data
    })


class GameMetricsDailyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    游戏每日指标视图集（只读）
    """
    queryset = GameMetricsDaily.objects.all()
    serializer_class = GameMetricsDailySerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['game', 'date']
    ordering = ['-date']

