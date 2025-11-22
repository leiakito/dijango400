"""
Content Views - 内容创作模块视图
"""
from datetime import timedelta
from decimal import Decimal
import json
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from django.db import models
from django.db.models import Q, Count, F
from django.db.models.functions import TruncDate
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied, ValidationError
from config.permissions import IsAdmin, IsCreator, IsOwnerOrAdmin, IsOwnerOrReadOnly
from apps.system.models import SysConfig

# 激励金额系数，可按需调整
A_COEF = Decimal('1')   # 每千曝光金额
B_COEF = Decimal('1')   # 每个点赞金额
C_COEF = Decimal('1')   # 每个评论金额

DEFAULT_FORBIDDEN = ['违禁', '非法', '敏感词']


def get_forbidden_words():
    value = SysConfig.get_value('forbidden_words')
    if not value:
        return DEFAULT_FORBIDDEN
    try:
        parsed = json.loads(value)
        if isinstance(parsed, list):
            return parsed
    except Exception:
        pass
    return [v.strip() for v in value.split(',') if v.strip()] or DEFAULT_FORBIDDEN


def ensure_no_forbidden(text: str):
    if not text:
        return
    lower = text.lower()
    for w in get_forbidden_words():
        if w.lower() in lower:
            raise ValidationError({'detail': f'内容包含违禁词，请修改后再提交（命中词：{w}）'})

from .models import Strategy, StrategyCollection, ContentReview, MediaAsset, StrategyLike, StrategyViewEvent, StrategyComment, Incentive
from .serializers import (
    StrategyListSerializer, StrategyDetailSerializer, StrategyCreateSerializer,
    ContentReviewSerializer, MediaAssetSerializer, StrategyCommentSerializer, IncentiveSerializer
)
from .filters import StrategyFilter


class StrategyViewSet(viewsets.ModelViewSet):
    """
    游戏攻略视图集
    """
    queryset = Strategy.objects.select_related('author', 'game').all()
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = StrategyFilter
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'view_count', 'like_count']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """根据操作返回不同的序列化器"""
        if self.action == 'list':
            return StrategyListSerializer
        elif self.action == 'create':
            return StrategyCreateSerializer
        elif self.action == 'comments':
            return StrategyCommentSerializer
        return StrategyDetailSerializer

    def get_permissions(self):
        if self.action in ['create']:
            return [IsCreator()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsOwnerOrAdmin()]
        return [permissions.IsAuthenticatedOrReadOnly()]

    def get_queryset(self):
        user = self.request.user
        qs = Strategy.objects.select_related('author', 'game').all()

        if user.is_authenticated and user.is_admin():
            return qs
        if user.is_authenticated:
            return qs.filter(Q(status=Strategy.Status.APPROVED) | Q(author=user))
        return qs.filter(status=Strategy.Status.APPROVED)

    def perform_create(self, serializer):
        """创建攻略时自动设置作者"""
        ensure_no_forbidden(self.request.data.get('title') or '')
        ensure_no_forbidden(self.request.data.get('content') or '')
        serializer.save(author=self.request.user, status=Strategy.Status.PENDING)

    def perform_update(self, serializer):
        strategy = self.get_object()
        user = self.request.user
        if not (user.is_admin() or strategy.author == user):
            raise PermissionDenied('无权编辑该攻略')
        prev_status = strategy.status
        ensure_no_forbidden(self.request.data.get('title') or '')
        ensure_no_forbidden(self.request.data.get('content') or '')
        instance = serializer.save()
        # 被拒绝后再次编辑，重置为待审核
        if prev_status == Strategy.Status.REJECTED:
            instance.status = Strategy.Status.PENDING
            instance.publish_date = None
            instance.save(update_fields=['status', 'publish_date'])

    def retrieve(self, request, *args, **kwargs):
        """
        获取攻略详情，同时记录阅读量（作者自己的访问不计入）
        """
        instance = self.get_object()
        user = request.user if request.user.is_authenticated else None

        # 记录阅读量（包含作者自己的访问）
        Strategy.objects.filter(pk=instance.pk).update(view_count=F('view_count') + 1)
        ip = request.META.get('REMOTE_ADDR') or None
        StrategyViewEvent.objects.create(
            strategy=instance,
            user=user,
            ip_address=ip,
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        instance.refresh_from_db(fields=['view_count'])

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """点赞攻略"""
        strategy = self.get_object()
        user = request.user
        if not user.is_authenticated:
            return Response({'error': '请先登录'}, status=status.HTTP_401_UNAUTHORIZED)

        like, created = StrategyLike.objects.get_or_create(user=user, strategy=strategy)
        if not created:
            # 取消点赞
            like.delete()
            strategy.like_count = max(0, strategy.like_count - 1)
            strategy.save(update_fields=['like_count'])
            is_liked = False
            message = '已取消点赞'
        else:
            strategy.like_count += 1
            strategy.save(update_fields=['like_count'])
            is_liked = True
            message = '点赞成功'

        return Response({'message': message, 'is_liked': is_liked, 'like_count': strategy.like_count})

    @action(detail=True, methods=['post'])
    def collect(self, request, pk=None):
        """收藏/取消收藏攻略"""
        strategy = self.get_object()
        user = request.user
        
        if not user.is_authenticated:
            return Response(
                {'error': '请先登录'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        collection, created = StrategyCollection.objects.get_or_create(
            user=user,
            strategy=strategy
        )
        
        if not created:
            # 已经收藏，执行取消收藏
            collection.delete()
            strategy.collect_count = max(0, strategy.collect_count - 1)
            strategy.save(update_fields=['collect_count'])
            is_collected = False
            message = '取消收藏成功'
        else:
            # 新收藏
            strategy.collect_count += 1
            strategy.save(update_fields=['collect_count'])
            is_collected = True
            message = '收藏成功'
        
        # 清除用户的推荐缓存，以便下次获取时重新计算
        from apps.recommendations.services import recommendation_service
        recommendation_service.clear_user_recommendations_cache(user)
        
        return Response({'message': message, 'is_collected': is_collected, 'collect_count': strategy.collect_count})

    @action(detail=True, methods=['get', 'post'], url_path='comments')
    def comments(self, request, pk=None):
        """
        攻略评论列表 / 新增评论
        """
        strategy = self.get_object()

        if request.method == 'GET':
            qs = StrategyComment.objects.filter(strategy=strategy).select_related('user').order_by('-created_at')
            serializer = StrategyCommentSerializer(qs, many=True, context={'request': request})
            return Response(serializer.data)

        # POST
        if not request.user.is_authenticated:
            return Response({'error': '请先登录'}, status=status.HTTP_401_UNAUTHORIZED)

        content = (request.data.get('content') or '').strip()
        if not content:
            return Response({'error': '评论内容不能为空'}, status=status.HTTP_400_BAD_REQUEST)

        comment = StrategyComment.objects.create(
            strategy=strategy,
            user=request.user,
            content=content
        )
        Strategy.objects.filter(pk=strategy.pk).update(comment_count=F('comment_count') + 1)
        serializer = StrategyCommentSerializer(comment, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated], url_path='mine')
    def mine(self, request):
        """
        获取当前创作者的攻略列表
        支持分页/排序，默认按创建时间倒序
        """
        user = request.user
        qs = Strategy.objects.filter(author=user).order_by('-created_at')
        ordering = request.query_params.get('ordering')
        if ordering:
            qs = qs.order_by(ordering)
        page = self.paginate_queryset(qs)
        serializer = StrategyListSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated], url_path='stats')
    def stats(self, request, pk=None):
        """
        创作者数据面板 - 返回单篇攻略的统计与热度趋势
        GET /api/v1/content/strategies/{id}/stats/?days=14
        """
        strategy = self.get_object()
        user = request.user
        if not (user.is_admin() or strategy.author == user):
            raise PermissionDenied('仅作者可查看该数据')

        days = int(request.query_params.get('days', 14))
        days = max(1, min(days, 60))
        start_time = timezone.now() - timedelta(days=days - 1)

        # 阅读趋势
        view_trend = StrategyViewEvent.objects.filter(
            strategy=strategy,
            created_at__gte=start_time
        ).annotate(date=TruncDate('created_at')).values('date').annotate(count=Count('id')).order_by('date')

        # 点赞趋势
        like_trend = StrategyLike.objects.filter(
            strategy=strategy,
            created_at__gte=start_time
        ).annotate(date=TruncDate('created_at')).values('date').annotate(count=Count('id')).order_by('date')

        # 收藏趋势
        collect_trend = StrategyCollection.objects.filter(
            strategy=strategy,
            created_at__gte=start_time
        ).annotate(date=TruncDate('created_at')).values('date').annotate(count=Count('id')).order_by('date')

        # 评论趋势
        comment_trend = StrategyComment.objects.filter(
            strategy=strategy,
            created_at__gte=start_time
        ).annotate(date=TruncDate('created_at')).values('date').annotate(count=Count('id')).order_by('date')

        # 组装每日数据
        trend_map = {}
        for item in view_trend:
            trend_map[item['date']] = {'views': item['count'], 'likes': 0, 'collects': 0, 'comments': 0}
        for item in like_trend:
            trend_map.setdefault(item['date'], {'views': 0, 'likes': 0, 'collects': 0, 'comments': 0})
            trend_map[item['date']]['likes'] = item['count']
        for item in collect_trend:
            trend_map.setdefault(item['date'], {'views': 0, 'likes': 0, 'collects': 0, 'comments': 0})
            trend_map[item['date']]['collects'] = item['count']
        for item in comment_trend:
            trend_map.setdefault(item['date'], {'views': 0, 'likes': 0, 'collects': 0, 'comments': 0})
            trend_map[item['date']]['comments'] = item['count']

        trend = []
        current = start_time.date()
        today = timezone.now().date()
        while current <= today:
            info = trend_map.get(current, {'views': 0, 'likes': 0, 'collects': 0, 'comments': 0})
            trend.append({
                'date': current.isoformat(),
                'views': info['views'],
                'likes': info['likes'],
                'collects': info['collects'],
                'comments': info['comments']
            })
            current += timedelta(days=1)

        # 如果近期没有事件但已有累计数据，回填到今日，避免趋势全为 0
        if trend:
            views_sum = sum(i['views'] for i in trend)
            likes_sum = sum(i['likes'] for i in trend)
            collects_sum = sum(i['collects'] for i in trend)
            comments_sum = sum(i['comments'] for i in trend)
            today_entry = trend[-1]

            if strategy.view_count > views_sum:
                today_entry['views'] = strategy.view_count
            if strategy.like_count > likes_sum:
                today_entry['likes'] = strategy.like_count
            if strategy.collect_count > collects_sum:
                today_entry['collects'] = strategy.collect_count
            if strategy.comment_count > comments_sum:
                today_entry['comments'] = strategy.comment_count
        else:
            today = timezone.now().date().isoformat()
            trend = [{
                'date': today,
                'views': strategy.view_count,
                'likes': strategy.like_count,
                'collects': strategy.collect_count,
                'comments': strategy.comment_count
            }]

        return Response({
            'id': strategy.id,
            'title': strategy.title,
            'view_count': strategy.view_count,
            'like_count': strategy.like_count,
            'collect_count': strategy.collect_count,
            'comment_count': strategy.comment_count,
            'trend': trend
        })


class MediaAssetViewSet(viewsets.ModelViewSet):
    """
    攻略媒体资源（图片/视频）上传、删除
    """
    queryset = MediaAsset.objects.select_related('strategy', 'strategy__author')
    serializer_class = MediaAssetSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_authenticated and user.is_admin():
            return qs
        return qs.filter(strategy__author=user)

    def perform_create(self, serializer):
        strategy_id = self.request.data.get('strategy')
        if not strategy_id:
            raise ValidationError({'strategy': '必须指定关联的攻略ID'})
        media_type = self.request.data.get('media_type') or self.request.data.get('type')
        if not media_type:
            raise ValidationError({'media_type': '缺少媒体类型'})
        try:
            strategy = Strategy.objects.get(pk=strategy_id)
        except Strategy.DoesNotExist:
            raise ValidationError({'strategy': '攻略不存在'})

        user = self.request.user
        if not (user.is_admin() or strategy.author == user):
            raise PermissionDenied('无权上传该攻略的媒体资源')

        serializer.save(strategy=strategy, type=media_type)

    def perform_destroy(self, instance):
        user = self.request.user
        if not (user.is_admin() or instance.strategy.author == user):
            raise PermissionDenied('无权删除该媒体资源')
        return super().perform_destroy(instance)


class ContentReviewViewSet(viewsets.ModelViewSet):
    """
    内容审核视图集（管理员使用）
    """
    queryset = Strategy.objects.all()
    serializer_class = StrategyDetailSerializer
    permission_classes = [IsAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'game', 'author']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """管理员可以查看所有状态的攻略"""
        queryset = Strategy.objects.select_related('author', 'game').all()
        
        # 支持按状态筛选
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取审核统计信息"""
        from django.db.models import Count
        
        stats = {
            'total': Strategy.objects.count(),
            'pending': Strategy.objects.filter(status=Strategy.Status.PENDING).count(),
            'approved': Strategy.objects.filter(status=Strategy.Status.APPROVED).count(),
            'rejected': Strategy.objects.filter(status=Strategy.Status.REJECTED).count(),
        }
        
        return Response(stats)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """通过审核"""
        strategy = self.get_object()
        
        if strategy.status == Strategy.Status.APPROVED:
            return Response(
                {'error': '该攻略已通过审核'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 更新攻略状态
        strategy.status = Strategy.Status.APPROVED
        strategy.publish_date = timezone.now()
        strategy.save(update_fields=['status', 'publish_date'])
        
        # 创建审核记录
        ContentReview.objects.create(
            strategy=strategy,
            reviewer=request.user,
            decision=ContentReview.Decision.APPROVED
        )
        
        # 记录系统日志
        from apps.system.middleware import log_system_event
        log_system_event(
            level='INFO',
            module='content',
            message=f"内容审核通过: {strategy.title}",
            context={
                'strategy_id': strategy.id,
                'strategy_title': strategy.title,
                'author': strategy.author.username,
                'reviewer': request.user.username
            },
            user=request.user
        )
        
        return Response({
            'message': '审核通过',
            'strategy': StrategyDetailSerializer(strategy).data
        })
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """拒绝审核"""
        strategy = self.get_object()
        reason = request.data.get('reason', '')
        
        if not reason:
            return Response(
                {'error': '请填写拒绝原因'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if strategy.status == Strategy.Status.REJECTED:
            return Response(
                {'error': '该攻略已被拒绝'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 更新攻略状态
        strategy.status = Strategy.Status.REJECTED
        strategy.save(update_fields=['status'])
        
        # 创建审核记录
        ContentReview.objects.create(
            strategy=strategy,
            reviewer=request.user,
            decision=ContentReview.Decision.REJECTED,
            reason=reason
        )
        
        # 记录系统日志
        from apps.system.middleware import log_system_event
        log_system_event(
            level='WARNING',
            module='content',
            message=f"内容审核拒绝: {strategy.title}",
            context={
                'strategy_id': strategy.id,
                'strategy_title': strategy.title,
                'author': strategy.author.username,
                'reviewer': request.user.username,
                'reason': reason
            },
            user=request.user
        )
        
        return Response({
            'message': '已拒绝',
            'strategy': StrategyDetailSerializer(strategy).data
        })
    
    @action(detail=True, methods=['get'])
    def review_history(self, request, pk=None):
        """获取攻略的审核历史"""
        strategy = self.get_object()
        reviews = strategy.reviews.all()
        serializer = ContentReviewSerializer(reviews, many=True)
        return Response(serializer.data)


class IncentiveViewSet(viewsets.GenericViewSet):
    """
    创作者激励视图
    """
    queryset = Incentive.objects.select_related('author').all()
    serializer_class = IncentiveSerializer
    permission_classes = [permissions.IsAuthenticated]

    def _get_period(self, request):
        return request.query_params.get('period') or timezone.now().strftime('%Y-%m')

    def _get_period_range(self, period: str):
        # period format: YYYY-MM
        try:
            year, month = [int(i) for i in period.split('-')]
            start = timezone.datetime(year, month, 1, tzinfo=timezone.utc)
            if month == 12:
                end = timezone.datetime(year + 1, 1, 1, tzinfo=timezone.utc)
            else:
                end = timezone.datetime(year, month + 1, 1, tzinfo=timezone.utc)
            return start, end
        except Exception:
            now = timezone.now()
            start = timezone.datetime(now.year, now.month, 1, tzinfo=timezone.utc)
            if now.month == 12:
                end = timezone.datetime(now.year + 1, 1, 1, tzinfo=timezone.utc)
            else:
                end = timezone.datetime(now.year, now.month + 1, 1, tzinfo=timezone.utc)
            return start, end

    def _compute_performance(self, user, start, end):
        strategies = Strategy.objects.filter(
            author=user,
            status=Strategy.Status.APPROVED,
            publish_date__lt=end,
            publish_date__gte=start
        )
        exposure_total = strategies.aggregate(total=models.Sum('view_count'))['total'] or 0
        likes_total = strategies.aggregate(total=models.Sum('like_count'))['total'] or 0
        comments_total = strategies.aggregate(total=models.Sum('comment_count'))['total'] or 0
        publish_count = strategies.count()
        return {
            'exposure': exposure_total,
            'likes': likes_total,
            'comments': comments_total,
            'publish_count': publish_count
        }

    def _get_performance(self, user, period):
        start, end = self._get_period_range(period)
        return self._compute_performance(user, start, end)

    def _check_eligibility(self, perf):
        # 规则：至少 1 篇发布且点赞数 >= 1
        eligible = perf['publish_count'] >= 1 and perf['likes'] >= 1
        reason = '满足申请条件' if eligible else '需至少1篇发布且点赞大于等于1'
        return eligible, reason

    def _compute_reward_amount(self, incentive: Incentive):
        exposure_part = (Decimal(incentive.exposure) / Decimal('1000')) * A_COEF
        likes_part = Decimal(incentive.likes) * B_COEF
        comments_part = Decimal(incentive.comments) * C_COEF
        # 保留两位小数
        return (exposure_part + likes_part + comments_part).quantize(Decimal('0.01'))

    @action(detail=False, methods=['get'])
    def stats(self, request):
        user = request.user
        target_user = user
        if user.is_admin():
            user_id = request.query_params.get('user')
            if user_id:
                try:
                    target_user = get_user_model().objects.get(pk=user_id)
                except get_user_model().DoesNotExist:
                    return Response({'error': '用户不存在'}, status=status.HTTP_400_BAD_REQUEST)

        period = self._get_period(request)
        perf = self._get_performance(target_user, period)
        eligible, reason = self._check_eligibility(perf)
        latest = Incentive.objects.filter(author=target_user, period=period).order_by('-created_at').first()

        return Response({
            'period': period,
            **perf,
            'eligible': eligible,
            'eligibility_reason': reason,
            'latest_application': IncentiveSerializer(latest).data if latest else None
        })

    @action(detail=False, methods=['post'])
    def apply(self, request):
        user = request.user
        if not (user.is_creator() or user.is_admin()):
            raise PermissionDenied('只有创作者可以申请')
        period = self._get_period(request)
        existing = Incentive.objects.filter(author=user, period=period).exclude(status=Incentive.Status.REJECTED).first()
        if existing:
            return Response({'error': '当前周期已提交申请'}, status=status.HTTP_400_BAD_REQUEST)

        perf = self._get_performance(user, period)
        eligible, reason = self._check_eligibility(perf)
        incentive = Incentive.objects.create(
            author=user,
            period=period,
            exposure=perf['exposure'],
            likes=perf['likes'],
            comments=perf['comments'],
            publish_count=perf['publish_count'],
            status=Incentive.Status.APPLIED,
            reason='' if eligible else reason
        )
        return Response(IncentiveSerializer(incentive).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def history(self, request):
        user = request.user
        qs = Incentive.objects.select_related('author')
        if user.is_admin():
            author_id = request.query_params.get('user')
            if author_id:
                qs = qs.filter(author_id=author_id)
        else:
            qs = qs.filter(author=user)
        status_filter = request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        qs = qs.order_by('-created_at')
        serializer = IncentiveSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'], permission_classes=[IsAdmin])
    def review(self, request, pk=None):
        incentive = self.get_object()
        status_value = request.data.get('status')
        reason = request.data.get('reason', '')
        if status_value not in [Incentive.Status.APPROVED, Incentive.Status.REJECTED]:
            return Response({'error': '状态必须是 approved 或 rejected'}, status=status.HTTP_400_BAD_REQUEST)
        incentive.status = status_value
        incentive.reason = reason
        incentive.save(update_fields=['status', 'reason', 'updated_at'])
        return Response(IncentiveSerializer(incentive).data)

    @action(detail=True, methods=['patch'], permission_classes=[IsAdmin])
    def grant(self, request, pk=None):
        incentive = self.get_object()
        amount = request.data.get('reward_amount')
        if amount is not None:
            try:
                amount_value = Decimal(str(amount))
            except (TypeError, ValueError, ArithmeticError):
                return Response({'error': '激励金额不合法'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            amount_value = self._compute_reward_amount(incentive)

        incentive.reward_amount = amount_value
        incentive.status = Incentive.Status.GRANTED
        incentive.save(update_fields=['reward_amount', 'status', 'updated_at'])
        return Response(IncentiveSerializer(incentive).data)
