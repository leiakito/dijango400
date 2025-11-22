"""
Analytics Views - 管理员数据概览
"""
from datetime import timedelta
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from config.permissions import IsAdmin, IsAdminOrPublisher

from apps.users.models import User
from apps.content.models import Strategy
from apps.community.models import Post, Comment, Topic
from apps.games.models import Game
from .services import AnalyticsService

analytics_service = AnalyticsService()


def get_daily_counts(model, date_field='created_at', days=7, filters=None):
    filters = filters or {}
    today = timezone.now().date()
    start_date = today - timedelta(days=days - 1)
    counts = []
    for i in range(days):
        day = start_date + timedelta(days=i)
        day_start = timezone.datetime.combine(day, timezone.datetime.min.time(), tzinfo=timezone.utc)
        day_end = day_start + timedelta(days=1)
        day_filters = {
            f"{date_field}__gte": day_start,
            f"{date_field}__lt": day_end,
            **filters
        }
        counts.append(model.objects.filter(**day_filters).count())
    dates = [(start_date + timedelta(days=i)).isoformat() for i in range(days)]
    return dates, counts


@api_view(['GET'])
@permission_classes([IsAdminOrPublisher])
def overview(request):
    """管理员概览：用户/内容/社区趋势"""
    # 汇总
    summary = {
        'users_total': User.objects.count(),
        'creators': User.objects.filter(role=User.Role.CREATOR).count(),
        'strategies_total': Strategy.objects.count(),
        'posts_total': Post.objects.filter(is_deleted=False).count(),
        'comments_total': Comment.objects.filter(is_deleted=False).count(),
        'games_total': Game.objects.count()
    }

    # 趋势数据（近7天）
    days = int(request.query_params.get('days', 7))
    days = max(3, min(days, 30))
    dates, user_counts = get_daily_counts(User, 'register_time', days)
    _, strategy_counts = get_daily_counts(Strategy, 'created_at', days)
    _, post_counts = get_daily_counts(Post, 'created_at', days, filters={'is_deleted': False})
    _, comment_counts = get_daily_counts(Comment, 'created_at', days, filters={'is_deleted': False})

    # 热门话题
    hot_topics = list(
        Topic.objects.order_by('-heat', '-follow_count')[:5].values('id', 'name', 'heat', 'follow_count', 'post_count')
    )

    return Response({
        'summary': summary,
        'trend': {
            'dates': dates,
            'users': user_counts,
            'strategies': strategy_counts,
            'posts': post_counts,
            'comments': comment_counts
        },
        'topics': hot_topics
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAdminOrPublisher])
def publisher_overview(request):
    """发行商仪表盘数据"""
    publisher_id = request.query_params.get('publisher')
    if not publisher_id:
        return Response({'detail': 'publisher 参数必填'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        publisher_id = int(publisher_id)
    except (TypeError, ValueError):
        return Response({'detail': 'publisher 参数错误'}, status=status.HTTP_400_BAD_REQUEST)

    data = analytics_service.generate_publisher_stats(publisher_id)
    if not data:
        return Response({'detail': '找不到发行商'}, status=status.HTTP_404_NOT_FOUND)
    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAdminOrPublisher])
def heatmap(request):
    """热度分布热力图"""
    data = analytics_service.generate_heatmap_data()
    return Response(data, status=status.HTTP_200_OK)
