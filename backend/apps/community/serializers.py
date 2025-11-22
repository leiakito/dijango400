"""
Community serializers
"""
from rest_framework import serializers
from .models import Topic, Post, Comment, Reaction, TopicFollow, Report, Feedback
from apps.users.serializers import UserProfileSerializer


class TopicSerializer(serializers.ModelSerializer):
    """
    话题序列化器
    """
    class Meta:
        model = Topic
        fields = [
            'id', 'name', 'description', 'heat', 
            'follow_count', 'post_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'heat', 'follow_count', 'post_count', 'created_at', 'updated_at']


class PostListSerializer(serializers.ModelSerializer):
    """
    动态列表序列化器
    """
    author = UserProfileSerializer(read_only=True)
    topics = TopicSerializer(many=True, read_only=True)
    
    class Meta:
        model = Post
        fields = [
            'id', 'author', 'text', 'topics', 'game',
            'like_count', 'comment_count', 'share_count',
            'is_deleted', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'like_count', 'comment_count', 'share_count',
            'is_deleted', 'created_at', 'updated_at'
        ]


class PostDetailSerializer(serializers.ModelSerializer):
    """
    动态详情序列化器
    """
    author = UserProfileSerializer(read_only=True)
    topics = TopicSerializer(many=True, read_only=True)
    topic_ids = serializers.PrimaryKeyRelatedField(
        queryset=Topic.objects.all(),
        many=True,
        source='topics',
        write_only=True,
        required=False
    )
    mention_ids = serializers.PrimaryKeyRelatedField(
        queryset=__import__('apps.users.models', fromlist=['User']).User.objects.all(),
        many=True,
        source='mentions',
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Post
        fields = [
            'id', 'author', 'text', 'topics', 'topic_ids',
            'mentions', 'mention_ids', 'game',
            'like_count', 'comment_count', 'share_count',
            'is_deleted', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'author', 'like_count', 'comment_count', 'share_count',
            'is_deleted', 'created_at', 'updated_at'
        ]

    def validate(self, attrs):
        # 兼容 content 字段
        content_val = self.initial_data.get('content')
        if content_val and not attrs.get('text'):
            attrs['text'] = content_val
        if not attrs.get('text'):
            raise serializers.ValidationError({'text': '内容不能为空'})
        return super().validate(attrs)


class CommentSerializer(serializers.ModelSerializer):
    """
    评论序列化器
    """
    user = UserProfileSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    depth = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 'user', 'content', 'parent',
            'game', 'strategy', 'post',
            'like_count', 'is_deleted', 'created_at', 'replies', 'depth'
        ]
        read_only_fields = ['id', 'user', 'like_count', 'is_deleted', 'created_at']
    
    def get_replies(self, obj):
        """递归获取子评论，默认最大深度 3"""
        max_depth = self.context.get('max_depth', 3)
        current_depth = self.context.get('depth', 1)
        if current_depth >= max_depth:
            return []
        qs = obj.replies.filter(is_deleted=False).order_by('created_at')
        if not qs.exists():
            return []
        serializer = CommentSerializer(
            qs,
            many=True,
            context={**self.context, 'depth': current_depth + 1}
        )
        return serializer.data

    def get_depth(self, obj):
        return self.context.get('depth', 1)


class CommentCreateSerializer(serializers.ModelSerializer):
    """
    评论创建序列化器
    """
    class Meta:
        model = Comment
        fields = ['content', 'parent', 'game', 'strategy', 'post']


class ReactionSerializer(serializers.ModelSerializer):
    """
    互动序列化器
    """
    user = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = Reaction
        fields = ['id', 'user', 'type', 'content_type', 'object_id', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class TopicFollowSerializer(serializers.ModelSerializer):
    """
    话题关注序列化器
    """
    topic = TopicSerializer(read_only=True)
    topic_id = serializers.PrimaryKeyRelatedField(
        queryset=Topic.objects.all(),
        source='topic',
        write_only=True
    )
    
    class Meta:
        model = TopicFollow
        fields = ['id', 'user', 'topic', 'topic_id', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class ReportSerializer(serializers.ModelSerializer):
    """
    举报序列化器
    """
    reporter = UserProfileSerializer(read_only=True)
    handler = UserProfileSerializer(read_only=True)
    target_type = serializers.CharField(write_only=True, required=False)
    target_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Report
        fields = [
            'id', 'reporter', 'content_type', 'object_id', 'target_type', 'target_id',
            'content', 'status', 'handler', 'handle_result',
            'created_at', 'handled_at'
        ]
        read_only_fields = ['id', 'reporter', 'handler', 'handled_at', 'created_at', 'content_type', 'object_id']


class FeedbackSerializer(serializers.ModelSerializer):
    """
    反馈序列化器
    """
    user = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = Feedback
        fields = ['id', 'user', 'content', 'contact', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
