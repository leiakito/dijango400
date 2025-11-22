"""
Recommendation models - 算法配置/推荐记录/游戏指标
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class AlgoConfig(models.Model):
    """
    算法配置模型（单例模式）
    存储推荐算法的各种参数
    """
    # 热度权重
    alpha = models.FloatField(
        _('静态热度权重 α'),
        default=0.7,
        help_text='总热度 = α * 静态热度 + β * 动态热度'
    )
    beta = models.FloatField(
        _('动态热度权重 β'),
        default=0.3,
        help_text='总热度 = α * 静态热度 + β * 动态热度'
    )
    
    # 时间衰减
    decay_lambda = models.FloatField(
        _('时间衰减系数 λ'),
        default=0.05,
        help_text='衰减公式: exp(-λ * t)'
    )
    
    # 静态热度权重
    weight_download = models.FloatField(
        _('下载权重'),
        default=0.5
    )
    weight_follow = models.FloatField(
        _('关注权重'),
        default=0.3
    )
    weight_review = models.FloatField(
        _('评价权重'),
        default=0.2
    )
    
    # 动态热度权重
    weight_like = models.FloatField(
        _('点赞权重'),
        default=0.6
    )
    weight_comment = models.FloatField(
        _('评论权重'),
        default=0.4
    )
    
    # 推荐数量
    top_k = models.IntegerField(
        _('推荐数量 TopK'),
        default=10,
        help_text='每个榜单/推荐列表返回的游戏数量'
    )
    
    # 刷新频率（小时）
    refresh_hours = models.IntegerField(
        _('刷新频率（小时）'),
        default=24,
        help_text='推荐列表的刷新间隔'
    )
    
    updated_at = models.DateTimeField(
        _('更新时间'),
        auto_now=True
    )
    
    class Meta:
        db_table = 'algo_config'
        verbose_name = _('算法配置')
        verbose_name_plural = _('算法配置')
    
    def __str__(self):
        return f"算法配置 (α={self.alpha}, β={self.beta}, λ={self.decay_lambda})"
    
    @classmethod
    def get_config(cls):
        """获取配置（单例）"""
        config, created = cls.objects.get_or_create(pk=1)
        return config


class Recommendation(models.Model):
    """
    推荐记录模型
    存储为用户生成的个性化推荐
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recommendations',
        verbose_name=_('用户')
    )
    game = models.ForeignKey(
        'games.Game',
        on_delete=models.CASCADE,
        related_name='recommendations',
        verbose_name=_('游戏')
    )
    reason = models.JSONField(
        _('推荐理由'),
        default=dict,
        help_text='存储推荐原因，如匹配的标签、相似度分数等'
    )
    score = models.FloatField(
        _('推荐分数'),
        db_index=True,
        help_text='相似度或推荐强度分数'
    )
    generated_at = models.DateTimeField(
        _('生成时间'),
        auto_now_add=True,
        db_index=True
    )
    
    class Meta:
        db_table = 'recommendations'
        verbose_name = _('推荐记录')
        verbose_name_plural = _('推荐记录')
        ordering = ['user', '-score', '-generated_at']
        indexes = [
            models.Index(fields=['user', '-score']),
            models.Index(fields=['game', '-generated_at']),
            models.Index(fields=['-generated_at']),
        ]
    
    def __str__(self):
        return f"推荐 {self.game.name} 给 {self.user.username} (分数: {self.score:.2f})"


class GameMetricsDaily(models.Model):
    """
    游戏每日指标模型
    存储每日计算的游戏各项指标和热度分数
    """
    game = models.ForeignKey(
        'games.Game',
        on_delete=models.CASCADE,
        related_name='daily_metrics',
        verbose_name=_('游戏')
    )
    date = models.DateField(
        _('日期'),
        db_index=True
    )
    
    # 当日统计数据
    downloads = models.IntegerField(
        _('下载数'),
        default=0
    )
    follows = models.IntegerField(
        _('关注数'),
        default=0
    )
    reviews = models.IntegerField(
        _('评价数'),
        default=0
    )
    posts = models.IntegerField(
        _('帖子数'),
        default=0
    )
    likes = models.IntegerField(
        _('点赞数'),
        default=0
    )
    comments = models.IntegerField(
        _('评论数'),
        default=0
    )
    
    # 计算的热度分数
    heat_static = models.FloatField(
        _('静态热度分'),
        default=0.0,
        db_index=True
    )
    heat_dynamic = models.FloatField(
        _('动态热度分'),
        default=0.0,
        db_index=True
    )
    heat_total = models.FloatField(
        _('总热度分'),
        default=0.0,
        db_index=True
    )
    
    created_at = models.DateTimeField(
        _('创建时间'),
        auto_now_add=True
    )
    
    class Meta:
        db_table = 'game_metrics_daily'
        verbose_name = _('游戏每日指标')
        verbose_name_plural = _('游戏每日指标')
        ordering = ['-date', '-heat_total']
        unique_together = [['game', 'date']]
        indexes = [
            models.Index(fields=['game', '-date']),
            models.Index(fields=['date', '-heat_total']),
            models.Index(fields=['-heat_total']),
        ]
    
    def __str__(self):
        return f"{self.game.name} - {self.date} (热度: {self.heat_total:.2f})"


class UserInterest(models.Model):
    """
    用户兴趣模型
    存储用户对各标签的兴趣权重
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='interests',
        verbose_name=_('用户')
    )
    tag = models.ForeignKey(
        'games.Tag',
        on_delete=models.CASCADE,
        related_name='interested_users',
        verbose_name=_('标签')
    )
    weight = models.FloatField(
        _('权重'),
        default=0.0,
        help_text='用户对该标签的兴趣权重'
    )
    updated_at = models.DateTimeField(
        _('更新时间'),
        auto_now=True
    )
    
    class Meta:
        db_table = 'user_interests'
        verbose_name = _('用户兴趣')
        verbose_name_plural = _('用户兴趣')
        unique_together = [['user', 'tag']]
        indexes = [
            models.Index(fields=['user', '-weight']),
        ]
    
    def __str__(self):
        return f"{self.user.username} 对 {self.tag.name} 的兴趣: {self.weight:.2f}"

