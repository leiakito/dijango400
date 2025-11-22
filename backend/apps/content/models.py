"""
Content models - 攻略/媒体/审核
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Strategy(models.Model):
    """
    游戏攻略模型
    """
    class Status(models.TextChoices):
        PENDING = 'pending', _('待审核')
        APPROVED = 'approved', _('已通过')
        REJECTED = 'rejected', _('已拒绝')
    
    title = models.CharField(
        _('标题'),
        max_length=200,
        db_index=True
    )
    content = models.TextField(
        _('内容'),
        help_text='支持富文本'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='strategies',
        verbose_name=_('作者')
    )
    game = models.ForeignKey(
        'games.Game',
        on_delete=models.CASCADE,
        related_name='strategies',
        verbose_name=_('关联游戏')
    )
    status = models.CharField(
        _('状态'),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True
    )
    
    # 统计数据
    view_count = models.IntegerField(
        _('浏览量'),
        default=0
    )
    like_count = models.IntegerField(
        _('点赞数'),
        default=0
    )
    collect_count = models.IntegerField(
        _('收藏数'),
        default=0
    )
    comment_count = models.IntegerField(
        _('评论数'),
        default=0
    )
    
    publish_date = models.DateTimeField(
        _('发布时间'),
        null=True,
        blank=True,
        db_index=True
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
        db_table = 'strategies'
        verbose_name = _('攻略')
        verbose_name_plural = _('攻略')
        ordering = ['-publish_date', '-created_at']
        indexes = [
            models.Index(fields=['game', '-publish_date']),
            models.Index(fields=['author', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['-like_count']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.game.name}"


class MediaAsset(models.Model):
    """
    媒体资源模型（图片、视频）
    """
    class MediaType(models.TextChoices):
        IMAGE = 'image', _('图片')
        VIDEO = 'video', _('视频')
    
    strategy = models.ForeignKey(
        Strategy,
        on_delete=models.CASCADE,
        related_name='media_assets',
        verbose_name=_('关联攻略')
    )
    type = models.CharField(
        _('媒体类型'),
        max_length=20,
        choices=MediaType.choices
    )
    url = models.FileField(
        _('文件'),
        upload_to='strategies/%Y/%m/%d/',
        max_length=500
    )
    meta = models.JSONField(
        _('元数据'),
        default=dict,
        blank=True,
        help_text='存储文件大小、分辨率、时长等信息'
    )
    order = models.IntegerField(
        _('排序'),
        default=0,
        help_text='在攻略中的显示顺序'
    )
    created_at = models.DateTimeField(
        _('创建时间'),
        auto_now_add=True
    )
    
    class Meta:
        db_table = 'media_assets'
        verbose_name = _('媒体资源')
        verbose_name_plural = _('媒体资源')
        ordering = ['strategy', 'order', 'created_at']
        indexes = [
            models.Index(fields=['strategy', 'order']),
        ]
    
    def __str__(self):
        return f"{self.get_type_display()} - {self.strategy.title}"


class ContentReview(models.Model):
    """
    内容审核记录
    """
    class Decision(models.TextChoices):
        APPROVED = 'approved', _('通过')
        REJECTED = 'rejected', _('拒绝')
    
    strategy = models.ForeignKey(
        Strategy,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_('关联攻略')
    )
    auto_hit_keywords = models.JSONField(
        _('自动命中关键词'),
        default=list,
        blank=True,
        help_text='自动检测到的敏感词列表'
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviews',
        verbose_name=_('审核人')
    )
    decision = models.CharField(
        _('审核决定'),
        max_length=20,
        choices=Decision.choices
    )
    reason = models.TextField(
        _('审核原因'),
        null=True,
        blank=True,
        help_text='拒绝时需要填写原因'
    )
    reviewed_at = models.DateTimeField(
        _('审核时间'),
        auto_now_add=True,
        db_index=True
    )
    
    class Meta:
        db_table = 'content_reviews'
        verbose_name = _('内容审核')
        verbose_name_plural = _('内容审核')
        ordering = ['-reviewed_at']
        indexes = [
            models.Index(fields=['strategy', '-reviewed_at']),
            models.Index(fields=['reviewer', '-reviewed_at']),
        ]
    
    def __str__(self):
        return f"{self.strategy.title} - {self.get_decision_display()}"


class StrategyCollection(models.Model):
    """
    攻略收藏模型
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='strategy_collections',
        verbose_name=_('用户')
    )
    strategy = models.ForeignKey(
        Strategy,
        on_delete=models.CASCADE,
        related_name='collectors',
        verbose_name=_('攻略')
    )
    created_at = models.DateTimeField(
        _('收藏时间'),
        auto_now_add=True
    )
    
    class Meta:
        db_table = 'strategy_collections'
        verbose_name = _('攻略收藏')
        verbose_name_plural = _('攻略收藏')
        ordering = ['-created_at']
        unique_together = [['user', 'strategy']]
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} 收藏了 {self.strategy.title}"


class StrategyLike(models.Model):
    """
    攻略点赞记录
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='liked_strategies',
        verbose_name=_('用户')
    )
    strategy = models.ForeignKey(
        Strategy,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name=_('攻略')
    )
    created_at = models.DateTimeField(
        _('点赞时间'),
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        db_table = 'strategy_likes'
        verbose_name = _('攻略点赞')
        verbose_name_plural = _('攻略点赞')
        unique_together = [['user', 'strategy']]
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['strategy', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} 点赞了 {self.strategy.title}"


class StrategyViewEvent(models.Model):
    """
    攻略阅读事件，用于统计曝光和热度趋势
    """
    strategy = models.ForeignKey(
        Strategy,
        on_delete=models.CASCADE,
        related_name='view_events',
        verbose_name=_('攻略')
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='strategy_views',
        verbose_name=_('用户')
    )
    ip_address = models.GenericIPAddressField(
        _('IP地址'),
        null=True,
        blank=True
    )
    user_agent = models.CharField(
        _('User Agent'),
        max_length=500,
        blank=True,
        default=''
    )
    created_at = models.DateTimeField(
        _('阅读时间'),
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        db_table = 'strategy_view_events'
        verbose_name = _('攻略阅读事件')
        verbose_name_plural = _('攻略阅读事件')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['strategy', '-created_at'])
        ]

    def __str__(self):
        return f"{self.strategy.title} 被阅读"


class StrategyComment(models.Model):
    """
    攻略评论
    """
    strategy = models.ForeignKey(
        Strategy,
        on_delete=models.CASCADE,
        related_name='strategy_comments',
        verbose_name=_('攻略')
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='strategy_comments',
        verbose_name=_('用户')
    )
    content = models.TextField(
        _('评论内容'),
        max_length=1000
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
        db_table = 'strategy_comments'
        verbose_name = _('攻略评论')
        verbose_name_plural = _('攻略评论')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['strategy', '-created_at'])
        ]

    def __str__(self):
        return f"{self.user.username} 评论了 {self.strategy.title}"


class Incentive(models.Model):
    """
    创作者激励
    """
    class Status(models.TextChoices):
        APPLIED = 'applied', _('已申请')
        APPROVED = 'approved', _('已通过')
        REJECTED = 'rejected', _('已拒绝')
        GRANTED = 'granted', _('已发放')

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='creator_incentives',
        verbose_name=_('作者')
    )
    period = models.CharField(
        _('周期'),
        max_length=20,
        help_text='例如 2025-11 表示月份周期'
    )
    exposure = models.IntegerField(_('曝光'), default=0)
    likes = models.IntegerField(_('点赞'), default=0)
    comments = models.IntegerField(_('评论'), default=0)
    publish_count = models.IntegerField(_('发布数量'), default=0)
    status = models.CharField(
        _('状态'),
        max_length=20,
        choices=Status.choices,
        default=Status.APPLIED
    )
    reason = models.TextField(
        _('备注/拒绝原因'),
        blank=True,
        default=''
    )
    reward_amount = models.DecimalField(
        _('激励金额'),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        db_table = 'creator_incentives'
        verbose_name = _('创作者激励')
        verbose_name_plural = _('创作者激励')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['author', '-created_at'], name='creator_incentives_author_idx'),
            models.Index(fields=['period'], name='creator_incentives_period_idx')
        ]

    def __str__(self):
        return f"{self.author.username} {self.period} {self.get_status_display()}"
