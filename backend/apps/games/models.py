"""
Game models - 发行商/游戏/标签/收藏
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class Publisher(models.Model):
    """
    发行商模型
    """
    name = models.CharField(
        _('发行商名称'),
        max_length=200,
        unique=True,
        db_index=True
    )
    contact_info = models.CharField(
        _('联系方式'),
        max_length=500,
        null=True,
        blank=True
    )
    logo = models.ImageField(
        _('Logo'),
        upload_to='publishers/%Y/%m/',
        null=True,
        blank=True
    )
    description = models.TextField(
        _('简介'),
        blank=True,
        default=''
    )
    website = models.URLField(
        _('官网'),
        max_length=500,
        blank=True,
        default=''
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
        db_table = 'publishers'
        verbose_name = _('发行商')
        verbose_name_plural = _('发行商')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Tag(models.Model):
    """
    游戏标签模型
    """
    name = models.CharField(
        _('标签名称'),
        max_length=50,
        unique=True,
        db_index=True
    )
    description = models.CharField(
        _('标签描述'),
        max_length=200,
        blank=True,
        default=''
    )
    created_at = models.DateTimeField(
        _('创建时间'),
        auto_now_add=True
    )
    
    class Meta:
        db_table = 'tags'
        verbose_name = _('标签')
        verbose_name_plural = _('标签')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Game(models.Model):
    """
    游戏模型
    """
    name = models.CharField(
        _('游戏名称'),
        max_length=200,
        db_index=True
    )
    category = models.CharField(
        _('游戏类别'),
        max_length=100,
        db_index=True,
        help_text='如：动作、冒险、角色扮演、策略等'
    )
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.CASCADE,
        related_name='games',
        verbose_name=_('发行商')
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='games',
        verbose_name=_('标签'),
        blank=True
    )
    
    # 统计数据
    rating = models.FloatField(
        _('评分'),
        default=0.0,
        db_index=True,
        help_text='0-10分'
    )
    download_count = models.IntegerField(
        _('下载数'),
        default=0,
        db_index=True
    )
    follow_count = models.IntegerField(
        _('关注数'),
        default=0,
        db_index=True
    )
    review_count = models.IntegerField(
        _('评价数'),
        default=0,
        db_index=True
    )
    
    # 游戏信息
    release_date = models.DateField(
        _('发行日期'),
        null=True,
        blank=True,
        db_index=True
    )
    online_time = models.DateField(
        _('上线时间'),
        null=True,
        blank=True
    )
    version = models.CharField(
        _('版本号'),
        max_length=50,
        null=True,
        blank=True
    )
    description = models.TextField(
        _('游戏描述'),
        blank=True,
        default=''
    )
    cover_image = models.ImageField(
        _('封面图'),
        upload_to='games/covers/%Y/%m/',
        null=True,
        blank=True
    )
    
    # 热度分数（由算法计算）
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
    updated_at = models.DateTimeField(
        _('更新时间'),
        auto_now=True
    )
    
    class Meta:
        db_table = 'games'
        verbose_name = _('游戏')
        verbose_name_plural = _('游戏')
        ordering = ['-heat_total', '-created_at']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['-rating']),
            models.Index(fields=['-download_count']),
            models.Index(fields=['-heat_total']),
            models.Index(fields=['publisher']),
            models.Index(fields=['-release_date']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.category})"


class GameScreenshot(models.Model):
    """
    游戏截图模型
    """
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        related_name='screenshots',
        verbose_name=_('游戏')
    )
    image = models.ImageField(
        _('截图'),
        upload_to='games/screenshots/%Y/%m/'
    )
    title = models.CharField(
        _('标题'),
        max_length=200,
        blank=True,
        default=''
    )
    description = models.TextField(
        _('描述'),
        blank=True,
        default=''
    )
    order = models.IntegerField(
        _('排序'),
        default=0,
        help_text='显示顺序，数字越小越靠前'
    )
    created_at = models.DateTimeField(
        _('创建时间'),
        auto_now_add=True
    )
    
    class Meta:
        db_table = 'game_screenshots'
        verbose_name = _('游戏截图')
        verbose_name_plural = _('游戏截图')
        ordering = ['game', 'order', '-created_at']
        indexes = [
            models.Index(fields=['game', 'order']),
        ]
    
    def __str__(self):
        return f"{self.game.name} - 截图 {self.order}"


class Collection(models.Model):
    """
    用户收藏游戏模型
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='collections',
        verbose_name=_('用户')
    )
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        related_name='collectors',
        verbose_name=_('游戏')
    )
    created_at = models.DateTimeField(
        _('收藏时间'),
        auto_now_add=True,
        db_index=True
    )
    
    class Meta:
        db_table = 'collections'
        verbose_name = _('收藏')
        verbose_name_plural = _('收藏')
        ordering = ['-created_at']
        unique_together = [['user', 'game']]
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['game', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} 收藏了 {self.game.name}"


class SinglePlayerRanking(models.Model):
    """
    单机游戏排行榜（3DM 数据）
    """
    source = models.CharField(
        _('来源'),
        max_length=50,
        default='3dm',
        db_index=True
    )
    rank = models.PositiveIntegerField(
        _('排名'),
        db_index=True
    )
    name = models.CharField(
        _('游戏名称'),
        max_length=200
    )
    english_name = models.CharField(
        _('英文名称'),
        max_length=200,
        blank=True,
        default=''
    )
    developer = models.CharField(
        _('开发商'),
        max_length=200,
        blank=True,
        default=''
    )
    publisher_name = models.CharField(
        _('发行商'),
        max_length=200,
        blank=True,
        default=''
    )
    genre = models.CharField(
        _('类型'),
        max_length=100,
        blank=True,
        default=''
    )
    platforms = models.CharField(
        _('平台'),
        max_length=200,
        blank=True,
        default=''
    )
    language = models.CharField(
        _('语言'),
        max_length=200,
        blank=True,
        default=''
    )
    release_date = models.DateField(
        _('发售日期'),
        null=True,
        blank=True
    )
    score = models.DecimalField(
        _('玩家评分'),
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        help_text='0-10 分'
    )
    rating_count = models.PositiveIntegerField(
        _('评分人数'),
        default=0
    )
    tags = models.JSONField(
        _('标签'),
        default=list,
        blank=True
    )
    cover_url = models.URLField(
        _('封面图'),
        max_length=500,
        blank=True,
        default=''
    )
    detail_url = models.URLField(
        _('来源链接'),
        max_length=500,
        blank=True,
        default=''
    )
    game = models.ForeignKey(
        'Game',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rankings',
        verbose_name=_('关联游戏')
    )
    fetched_at = models.DateTimeField(
        _('抓取时间'),
        default=timezone.now,
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
        db_table = 'single_player_rankings'
        verbose_name = _('单机游戏排行榜')
        verbose_name_plural = _('单机游戏排行榜')
        ordering = ['source', 'rank']
        unique_together = [('source', 'rank')]
        indexes = [
            models.Index(fields=['source', 'rank']),
            models.Index(fields=['source', '-fetched_at'])
        ]

    def __str__(self):
        return f"{self.source} #{self.rank} - {self.name}"
