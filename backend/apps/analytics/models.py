"""
Analytics models - 采集/清洗/仪表盘缓存
"""
from django.db import models
from django.utils.translation import gettext_lazy as _


class RawCrawl(models.Model):
    """
    原始爬取数据模型
    存储从第三方平台抓取的原始数据
    """
    source = models.CharField(
        _('数据源'),
        max_length=100,
        db_index=True,
        help_text='如: steam, epic, gog 等'
    )
    payload = models.JSONField(
        _('数据载荷'),
        help_text='原始JSON数据'
    )
    hash = models.CharField(
        _('数据哈希'),
        max_length=64,
        unique=True,
        db_index=True,
        help_text='用于去重的数据哈希值'
    )
    created_at = models.DateTimeField(
        _('创建时间'),
        auto_now_add=True,
        db_index=True
    )
    
    class Meta:
        db_table = 'raw_crawls'
        verbose_name = _('原始爬取数据')
        verbose_name_plural = _('原始爬取数据')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['source', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.source} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class DashCardCache(models.Model):
    """
    仪表盘卡片缓存模型
    缓存各种统计图表的数据，供前端 ECharts 使用
    """
    key = models.CharField(
        _('缓存键'),
        max_length=200,
        unique=True,
        db_index=True,
        help_text='如: overview_trend, heatmap_category, publisher_stats 等'
    )
    snapshot = models.JSONField(
        _('数据快照'),
        help_text='ECharts 配置或数据对象'
    )
    description = models.CharField(
        _('描述'),
        max_length=500,
        blank=True,
        default=''
    )
    updated_at = models.DateTimeField(
        _('更新时间'),
        auto_now=True,
        db_index=True
    )
    
    class Meta:
        db_table = 'dash_card_cache'
        verbose_name = _('仪表盘缓存')
        verbose_name_plural = _('仪表盘缓存')
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.key} (更新于 {self.updated_at.strftime('%Y-%m-%d %H:%M')})"


class CrawlJob(models.Model):
    """
    爬虫任务记录
    记录每次爬虫任务的执行情况
    """
    class Status(models.TextChoices):
        RUNNING = 'running', _('运行中')
        SUCCESS = 'success', _('成功')
        FAILED = 'failed', _('失败')
    
    source = models.CharField(
        _('数据源'),
        max_length=100,
        db_index=True
    )
    status = models.CharField(
        _('状态'),
        max_length=20,
        choices=Status.choices,
        default=Status.RUNNING,
        db_index=True
    )
    items_count = models.IntegerField(
        _('抓取条数'),
        default=0
    )
    error_message = models.TextField(
        _('错误信息'),
        blank=True,
        default=''
    )
    started_at = models.DateTimeField(
        _('开始时间'),
        auto_now_add=True,
        db_index=True
    )
    finished_at = models.DateTimeField(
        _('结束时间'),
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'crawl_jobs'
        verbose_name = _('爬虫任务')
        verbose_name_plural = _('爬虫任务')
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['source', '-started_at']),
            models.Index(fields=['status', '-started_at']),
        ]
    
    def __str__(self):
        return f"{self.source} - {self.get_status_display()} ({self.started_at.strftime('%Y-%m-%d %H:%M')})"
    
    @property
    def duration(self):
        """计算任务执行时长"""
        if self.finished_at:
            return (self.finished_at - self.started_at).total_seconds()
        return None

