"""
Community models - 动态/评论/互动/话题/举报反馈
"""
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _


class Topic(models.Model):
    """
    话题模型
    """
    name = models.CharField(
        _('话题名称'),
        max_length=100,
        unique=True,
        db_index=True
    )
    description = models.TextField(
        _('话题描述'),
        blank=True,
        default=''
    )
    heat = models.FloatField(
        _('热度'),
        default=0.0,
        db_index=True
    )
    follow_count = models.IntegerField(
        _('关注数'),
        default=0
    )
    post_count = models.IntegerField(
        _('帖子数'),
        default=0
    )
    created_at = models.DateTimeField(
        _('创建时间'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('更新时间'),
        auto_now=True
    )
    
    class Meta:
        db_table = 'topics'
        verbose_name = _('话题')
        verbose_name_plural = _('话题')
        ordering = ['-heat', '-created_at']
        indexes = [
            models.Index(fields=['-heat']),
            models.Index(fields=['-post_count']),
        ]
    
    def __str__(self):
        return f"#{self.name}"


class Post(models.Model):
    """
    动态/帖子模型
    """
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name=_('作者')
    )
    text = models.TextField(
        _('内容'),
        max_length=5000
    )
    topics = models.ManyToManyField(
        Topic,
        related_name='posts',
        verbose_name=_('话题'),
        blank=True
    )
    mentions = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='mentioned_in_posts',
        verbose_name=_('提及用户'),
        blank=True
    )
    
    # 关联游戏（可选）
    game = models.ForeignKey(
        'games.Game',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts',
        verbose_name=_('关联游戏')
    )
    
    # 统计数据
    like_count = models.IntegerField(
        _('点赞数'),
        default=0
    )
    comment_count = models.IntegerField(
        _('评论数'),
        default=0
    )
    share_count = models.IntegerField(
        _('分享数'),
        default=0
    )
    
    is_deleted = models.BooleanField(
        _('是否删除'),
        default=False,
        db_index=True
    )
    created_at = models.DateTimeField(
        _('创建时间'),
        auto_now_add=True,
        db_index=True
    )
    updated_at = models.DateTimeField(
        _('更新时间'),
        auto_now=True
    )
    
    class Meta:
        db_table = 'posts'
        verbose_name = _('动态')
        verbose_name_plural = _('动态')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['author', '-created_at']),
            models.Index(fields=['game', '-created_at']),
            models.Index(fields=['is_deleted', '-created_at']),
            models.Index(fields=['-like_count']),
        ]
    
    def __str__(self):
        return f"{self.author.username}: {self.text[:50]}"


class Comment(models.Model):
    """
    评论模型（支持多级评论）
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_('用户')
    )
    content = models.TextField(
        _('评论内容'),
        max_length=2000
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name=_('父评论'),
        db_index=True
    )
    
    # 评论目标（使用 GenericForeignKey 支持多种对象）
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        db_index=True
    )
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # 兼容旧字段（可选）
    game = models.ForeignKey(
        'games.Game',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='comments',
        verbose_name=_('游戏')
    )
    strategy = models.ForeignKey(
        'content.Strategy',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='comments',
        verbose_name=_('攻略')
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='comments',
        verbose_name=_('动态')
    )
    
    like_count = models.IntegerField(
        _('点赞数'),
        default=0
    )
    is_deleted = models.BooleanField(
        _('是否删除'),
        default=False
    )
    created_at = models.DateTimeField(
        _('创建时间'),
        auto_now_add=True,
        db_index=True
    )
    
    class Meta:
        db_table = 'comments'
        verbose_name = _('评论')
        verbose_name_plural = _('评论')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['content_type', 'object_id', '-created_at']),
            models.Index(fields=['game', '-created_at']),
            models.Index(fields=['strategy', '-created_at']),
            models.Index(fields=['post', '-created_at']),
            models.Index(fields=['parent', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username}: {self.content[:50]}"


class Reaction(models.Model):
    """
    互动模型（点赞/踩）
    """
    class ReactionType(models.TextChoices):
        LIKE = 'like', _('点赞')
        DISLIKE = 'dislike', _('踩')
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reactions',
        verbose_name=_('用户')
    )
    type = models.CharField(
        _('互动类型'),
        max_length=20,
        choices=ReactionType.choices
    )
    
    # 互动目标（使用 GenericForeignKey）
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField(
        db_index=True
    )
    content_object = GenericForeignKey('content_type', 'object_id')
    
    created_at = models.DateTimeField(
        _('创建时间'),
        auto_now_add=True
    )
    
    class Meta:
        db_table = 'reactions'
        verbose_name = _('互动')
        verbose_name_plural = _('互动')
        ordering = ['-created_at']
        unique_together = [['user', 'content_type', 'object_id', 'type']]
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} {self.get_type_display()}"


class TopicFollow(models.Model):
    """
    话题关注模型
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='topic_follows',
        verbose_name=_('用户')
    )
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name=_('话题')
    )
    created_at = models.DateTimeField(
        _('关注时间'),
        auto_now_add=True
    )
    
    class Meta:
        db_table = 'topic_follows'
        verbose_name = _('话题关注')
        verbose_name_plural = _('话题关注')
        ordering = ['-created_at']
        unique_together = [['user', 'topic']]
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['topic', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} 关注了 {self.topic.name}"


class Report(models.Model):
    """
    举报模型
    """
    class Status(models.TextChoices):
        PENDING = 'pending', _('待处理')
        RESOLVED = 'resolved', _('已处理')
    
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reports',
        verbose_name=_('举报人')
    )
    
    # 举报目标
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField(
        db_index=True
    )
    content_object = GenericForeignKey('content_type', 'object_id')
    
    content = models.TextField(
        _('举报内容'),
        help_text='举报原因说明'
    )
    status = models.CharField(
        _('处理状态'),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True
    )
    handler = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='handled_reports',
        verbose_name=_('处理人')
    )
    handle_result = models.TextField(
        _('处理结果'),
        blank=True,
        default=''
    )
    created_at = models.DateTimeField(
        _('举报时间'),
        auto_now_add=True,
        db_index=True
    )
    handled_at = models.DateTimeField(
        _('处理时间'),
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'reports'
        verbose_name = _('举报')
        verbose_name_plural = _('举报')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['reporter', '-created_at']),
            models.Index(fields=['content_type', 'object_id']),
        ]
    
    def __str__(self):
        return f"{self.reporter.username} 举报 - {self.get_status_display()}"


class Feedback(models.Model):
    """
    用户反馈模型
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='feedbacks',
        verbose_name=_('用户')
    )
    content = models.TextField(
        _('反馈内容')
    )
    contact = models.CharField(
        _('联系方式'),
        max_length=200,
        blank=True,
        default=''
    )
    created_at = models.DateTimeField(
        _('反馈时间'),
        auto_now_add=True,
        db_index=True
    )
    
    class Meta:
        db_table = 'feedbacks'
        verbose_name = _('反馈')
        verbose_name_plural = _('反馈')
        ordering = ['-created_at']
    
    def __str__(self):
        user_str = self.user.username if self.user else '匿名'
        return f"{user_str} 的反馈"

