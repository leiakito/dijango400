"""
Community Views - 社区互动模块视图
"""
import json
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import F, Q
from django.utils import timezone

from .models import Post, Comment, Topic, Reaction, TopicFollow, Report, Feedback
from .serializers import (
    PostListSerializer, PostDetailSerializer,
    CommentSerializer, CommentCreateSerializer,
    TopicSerializer, ReactionSerializer, TopicFollowSerializer,
    ReportSerializer, FeedbackSerializer
)
from .filters import PostFilter, TopicFilter
from config.permissions import IsAdmin
from apps.content.models import Strategy
from apps.games.models import Game
from apps.system.models import SysConfig

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
    # 兼容逗号分隔
    return [v.strip() for v in value.split(',') if v.strip()] or DEFAULT_FORBIDDEN


def ensure_no_forbidden(text: str):
    if not text:
        return
    lower = text.lower()
    for w in get_forbidden_words():
        if w.lower() in lower:
            raise ValidationError({'detail': f'内容包含违禁词，请修改后再发布（命中词：{w}）'})


def recalc_topic_metrics(topic: Topic):
    """根据帖子和关注数更新话题热度与帖子数"""
    post_count = topic.posts.filter(is_deleted=False).count()
    follow_count = topic.follow_count
    heat = post_count + follow_count * 2
    Topic.objects.filter(pk=topic.pk).update(post_count=post_count, heat=heat)


class PostViewSet(viewsets.ModelViewSet):
    """
    社区动态视图集
    """
    queryset = Post.objects.filter(is_deleted=False)
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PostFilter
    search_fields = ['text']
    ordering_fields = ['created_at', 'like_count', 'comment_count']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """根据操作返回不同的序列化器"""
        if self.action == 'list':
            return PostListSerializer
        return PostDetailSerializer

    def get_permissions(self):
        if self.action in ['create', 'like', 'dislike']:
            return [permissions.IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    def perform_create(self, serializer):
        """创建动态时自动设置作者"""
        ensure_no_forbidden(self.request.data.get('text') or self.request.data.get('content') or '')
        instance = serializer.save(author=self.request.user)
        # 更新话题帖子数/热度
        for topic in instance.topics.all():
            recalc_topic_metrics(topic)

    def perform_update(self, serializer):
        post = self.get_object()
        user = self.request.user
        if not (user.is_authenticated and (user.is_admin() or user == post.author)):
            raise permissions.PermissionDenied('无权编辑该动态')
        ensure_no_forbidden(self.request.data.get('text') or self.request.data.get('content') or '')
        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        if not (user.is_authenticated and (user.is_admin() or user == instance.author)):
            raise permissions.PermissionDenied('无权删除该动态')
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted'])
        for topic in instance.topics.all():
            recalc_topic_metrics(topic)

    def _toggle_reaction(self, request, reaction_type):
        post = self.get_object()
        user = request.user
        if not user.is_authenticated:
            return Response({'error': '请先登录'}, status=status.HTTP_401_UNAUTHORIZED)
        result = ReactionViewSet.toggle_reaction(user, post, reaction_type)
        return Response(result)

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """点赞动态（幂等）"""
        return self._toggle_reaction(request, Reaction.ReactionType.LIKE)

    @action(detail=True, methods=['post'])
    def dislike(self, request, pk=None):
        """踩动态（幂等）"""
        return self._toggle_reaction(request, Reaction.ReactionType.DISLIKE)


class CommentViewSet(viewsets.ModelViewSet):
    """
    评论视图集
    """
    queryset = Comment.objects.filter(is_deleted=False)
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['created_at']

    def get_serializer_class(self):
        """根据操作返回不同的序列化器"""
        if self.action == 'create':
            return CommentCreateSerializer
        return CommentSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    def get_queryset(self):
        qs = Comment.objects.filter(is_deleted=False)
        target = self.request.query_params.get('target')
        target_id = self.request.query_params.get('target_id')
        if target and target_id:
            if target == 'post':
                qs = qs.filter(post_id=target_id).filter(Q(parent__isnull=True) | Q(parent__is_deleted=True))
            elif target == 'strategy':
                qs = qs.filter(strategy_id=target_id).filter(Q(parent__isnull=True) | Q(parent__is_deleted=True))
            elif target == 'game':
                qs = qs.filter(game_id=target_id).filter(Q(parent__isnull=True) | Q(parent__is_deleted=True))
        ordering = self.request.query_params.get('ordering')
        if ordering == 'hot':
            qs = qs.order_by('-like_count', '-created_at')
        return qs

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = CommentSerializer(page, many=True, context={'request': request, 'depth': 1, 'max_depth': 5})
        return self.get_paginated_response(serializer.data)

    def perform_create(self, serializer):
        """创建评论时自动设置作者，并写入目标"""
        request_data = self.request.data
        target_type = request_data.get('target') or request_data.get('target_type')
        target_id = request_data.get('target_id')

        # 将 target 映射到对应字段
        extra_kwargs = {}
        if target_type and target_id:
            if target_type == 'post':
                extra_kwargs['post_id'] = target_id
            elif target_type == 'strategy':
                extra_kwargs['strategy_id'] = target_id
            elif target_type == 'game':
                extra_kwargs['game_id'] = target_id

        ensure_no_forbidden(request_data.get('content') or '')
        comment = serializer.save(user=self.request.user, **extra_kwargs)

        # 更新评论计数
        if comment.post_id:
            Post.objects.filter(pk=comment.post_id).update(comment_count=F('comment_count') + 1)
        if comment.strategy_id:
            Strategy.objects.filter(pk=comment.strategy_id).update(comment_count=F('comment_count') + 1)

    def perform_destroy(self, instance):
        user = self.request.user
        if not (user.is_authenticated and (user.is_admin() or user == instance.user)):
            raise permissions.PermissionDenied('无权删除该评论')
        # 更新计数
        if instance.post_id:
            Post.objects.filter(pk=instance.post_id).update(comment_count=F('comment_count') - 1)
        if instance.strategy_id:
            Strategy.objects.filter(pk=instance.strategy_id).update(comment_count=F('comment_count') - 1)
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted'])

    def destroy(self, request, *args, **kwargs):
        """允许删除任意评论（含回复），避免因筛选导致找不到"""
        comment = Comment.objects.filter(pk=kwargs.get('pk')).first()
        if not comment:
            return Response({'detail': '评论不存在'}, status=status.HTTP_404_NOT_FOUND)
        if not (request.user.is_authenticated and (request.user.is_admin() or request.user == comment.user)):
            return Response({'detail': '无权删除该评论'}, status=status.HTTP_403_FORBIDDEN)
        # 复用软删逻辑
        self.perform_destroy(comment)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TopicViewSet(viewsets.ModelViewSet):
    """
    话题视图集
    """
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = TopicFilter
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'follow_count', 'heat']
    ordering = ['-heat']

    @action(detail=True, methods=['post'])
    def follow(self, request, pk=None):
        """关注话题"""
        topic = self.get_object()
        user = request.user
        if not user.is_authenticated:
            return Response({'error': '请先登录'}, status=status.HTTP_401_UNAUTHORIZED)
        follow, created = TopicFollow.objects.get_or_create(user=user, topic=topic)
        if not created:
            follow.delete()
            Topic.objects.filter(pk=topic.pk).update(follow_count=F('follow_count') - 1)
            recalc_topic_metrics(topic)
            return Response({'message': '已取消关注', 'is_following': False})
        Topic.objects.filter(pk=topic.pk).update(follow_count=F('follow_count') + 1)
        recalc_topic_metrics(topic)
        return Response({'message': '关注成功', 'is_following': True})

    @action(detail=False, methods=['get'])
    def hot(self, request):
        """热门话题"""
        qs = Topic.objects.order_by('-heat', '-follow_count')[:20]
        data = TopicSerializer(qs, many=True).data
        return Response(data)

    def perform_create(self, serializer):
        ensure_no_forbidden(self.request.data.get('name') or '')
        ensure_no_forbidden(self.request.data.get('description') or '')
        serializer.save()

    def perform_update(self, serializer):
        ensure_no_forbidden(self.request.data.get('name') or '')
        ensure_no_forbidden(self.request.data.get('description') or '')
        serializer.save()


class ReactionViewSet(viewsets.GenericViewSet):
    """
    点赞/踩视图（通用）
    """
    queryset = Reaction.objects.all()
    serializer_class = ReactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    @staticmethod
    def _get_target(target_type: str, target_id: int):
        mapping = {
            'post': Post,
            'comment': Comment,
            'strategy': Strategy,
            'game': Game
        }
        model = mapping.get(target_type)
        if not model:
            return None
        try:
            return model.objects.get(pk=target_id)
        except model.DoesNotExist:
            return None

    @staticmethod
    def toggle_reaction(user, target, reaction_type):
        ctype = ContentType.objects.get_for_model(target.__class__)
        qs = Reaction.objects.filter(user=user, content_type=ctype, object_id=target.id)
        existing = qs.first()

        with transaction.atomic():
            if existing:
                if existing.type == reaction_type:
                    if existing.type == Reaction.ReactionType.LIKE and hasattr(target, 'like_count'):
                        target.__class__.objects.filter(pk=target.pk).update(like_count=F('like_count') - 1)
                    existing.delete()
                    refreshed = target.__class__.objects.filter(pk=target.pk).values_list('like_count', flat=True).first() if hasattr(target, 'like_count') else None
                    return {
                        'message': '已取消',
                        'is_liked': False,
                        'is_disliked': False,
                        'like_count': refreshed
                    }
                else:
                    if existing.type == Reaction.ReactionType.LIKE and hasattr(target, 'like_count'):
                        target.__class__.objects.filter(pk=target.pk).update(like_count=F('like_count') - 1)
                    existing.type = reaction_type
                    existing.save(update_fields=['type'])
            else:
                qs.create(user=user, type=reaction_type, content_type=ctype, object_id=target.id)

            if reaction_type == Reaction.ReactionType.LIKE and hasattr(target, 'like_count'):
                target.__class__.objects.filter(pk=target.pk).update(like_count=F('like_count') + 1)

        refreshed = target.__class__.objects.filter(pk=target.pk).values_list('like_count', flat=True).first() if hasattr(target, 'like_count') else None
        return {
            'message': '操作成功',
            'is_liked': reaction_type == Reaction.ReactionType.LIKE,
            'is_disliked': reaction_type == Reaction.ReactionType.DISLIKE,
            'like_count': refreshed
        }

    def create(self, request, *args, **kwargs):
        user = request.user
        target_type = request.data.get('target_type') or request.data.get('target')
        target_id = request.data.get('target_id')
        reaction_type = request.data.get('type')

        if not target_type or not target_id or reaction_type not in Reaction.ReactionType.values:
            return Response({'error': '缺少参数或类型错误'}, status=status.HTTP_400_BAD_REQUEST)

        target = self._get_target(target_type, target_id)
        if not target:
            return Response({'error': '目标不存在'}, status=status.HTTP_404_NOT_FOUND)

        result = self.toggle_reaction(user, target, reaction_type)
        return Response(result)


class ReportViewSet(viewsets.ModelViewSet):
    """
    举报视图
    """
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status']
    ordering = ['-created_at']

    def get_permissions(self):
        if self.action in ['create']:
            return [permissions.IsAuthenticated()]
        elif self.action in ['list', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return super().get_permissions()

    def perform_create(self, serializer):
        data = serializer.validated_data
        target_type = data.pop('target_type', None)
        target_id = data.pop('target_id', None)
        if target_type and target_id:
            mapping = {
                'post': Post,
                'comment': Comment,
                'strategy': Strategy,
                'game': Game
            }
            model = mapping.get(target_type)
            if model:
                data['content_type'] = ContentType.objects.get_for_model(model)
                data['object_id'] = target_id
        serializer.save(reporter=self.request.user, **data)

    def perform_update(self, serializer):
        # 支持处理时删除目标
        action_param = self.request.data.get('action')
        instance = serializer.save(handler=self.request.user, handled_at=timezone.now())

        if action_param == 'delete_target':
            # 删除对应对象（软删）
            ctype = instance.content_type
            target_id = instance.object_id
            model = ctype.model_class()
            if model:
                try:
                    target = model.objects.get(pk=target_id)
                    if isinstance(target, Post):
                        target.is_deleted = True
                        target.save(update_fields=['is_deleted'])
                    elif isinstance(target, Comment):
                        target.is_deleted = True
                        target.save(update_fields=['is_deleted'])
                    elif isinstance(target, Strategy):
                        target.status = Strategy.Status.REJECTED
                        target.save(update_fields=['status'])
                    elif isinstance(target, Topic):
                        target.delete()
                    instance.handle_result = (instance.handle_result or '') + ' | 已删除目标'
                    instance.save(update_fields=['handle_result'])
                except model.DoesNotExist:
                    pass


class FeedbackViewSet(viewsets.ModelViewSet):
    """
    反馈视图
    """
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer

    def get_permissions(self):
        if self.action in ['create']:
            return [permissions.IsAuthenticated()]
        elif self.action in ['list', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
