"""
System models - 系统参数/日志/备份/激励
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class SysLog(models.Model):
    """
    系统日志模型
    记录系统运行日志
    """
    class Level(models.TextChoices):
        DEBUG = 'DEBUG', _('调试')
        INFO = 'INFO', _('信息')
        WARNING = 'WARNING', _('警告')
        ERROR = 'ERROR', _('错误')
        CRITICAL = 'CRITICAL', _('严重')
    
    level = models.CharField(
        _('日志级别'),
        max_length=20,
        choices=Level.choices,
        db_index=True
    )
    module = models.CharField(
        _('模块'),
        max_length=100,
        db_index=True,
        help_text='产生日志的模块名称'
    )
    message = models.TextField(
        _('日志消息')
    )
    context = models.JSONField(
        _('上下文信息'),
        null=True,
        blank=True,
        help_text='额外的上下文数据'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sys_logs',
        verbose_name=_('相关用户')
    )
    ip_address = models.GenericIPAddressField(
        _('IP地址'),
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(
        _('创建时间'),
        auto_now_add=True,
        db_index=True
    )
    
    class Meta:
        db_table = 'sys_logs'
        verbose_name = _('系统日志')
        verbose_name_plural = _('系统日志')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['level', '-created_at']),
            models.Index(fields=['module', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"[{self.level}] {self.module} - {self.message[:50]}"


class SysConfig(models.Model):
    """
    系统配置模型
    存储系统级别的配置参数（键值对）
    """
    key = models.CharField(
        _('配置键'),
        max_length=100,
        unique=True,
        db_index=True
    )
    value = models.TextField(
        _('配置值'),
        help_text='可以是字符串或JSON格式'
    )
    description = models.CharField(
        _('描述'),
        max_length=500,
        blank=True,
        default=''
    )
    is_public = models.BooleanField(
        _('是否公开'),
        default=False,
        help_text='是否可以通过API公开访问'
    )
    updated_at = models.DateTimeField(
        _('更新时间'),
        auto_now=True
    )
    
    class Meta:
        db_table = 'sys_config'
        verbose_name = _('系统配置')
        verbose_name_plural = _('系统配置')
        ordering = ['key']
    
    def __str__(self):
        return f"{self.key} = {self.value[:50]}"
    
    @classmethod
    def get_value(cls, key, default=None):
        """获取配置值"""
        try:
            config = cls.objects.get(key=key)
            return config.value
        except cls.DoesNotExist:
            return default
    
    @classmethod
    def set_value(cls, key, value, description=''):
        """设置配置值"""
        config, created = cls.objects.update_or_create(
            key=key,
            defaults={'value': value, 'description': description}
        )
        return config


class BackupJob(models.Model):
    """
    备份任务模型
    记录数据库备份任务
    """
    class Status(models.TextChoices):
        RUNNING = 'running', _('运行中')
        SUCCESS = 'success', _('成功')
        FAILED = 'failed', _('失败')
    
    status = models.CharField(
        _('状态'),
        max_length=20,
        choices=Status.choices,
        default=Status.RUNNING,
        db_index=True
    )
    file_path = models.CharField(
        _('备份文件路径'),
        max_length=500,
        blank=True,
        default=''
    )
    file_size = models.BigIntegerField(
        _('文件大小（字节）'),
        null=True,
        blank=True
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
        db_table = 'backup_jobs'
        verbose_name = _('备份任务')
        verbose_name_plural = _('备份任务')
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['status', '-started_at']),
        ]
    
    def __str__(self):
        return f"备份 - {self.get_status_display()} ({self.started_at.strftime('%Y-%m-%d %H:%M')})"
    
    @property
    def duration(self):
        """计算任务执行时长"""
        if self.finished_at:
            return (self.finished_at - self.started_at).total_seconds()
        return None


class Incentive(models.Model):
    """
    创作者激励模型
    记录创作者的激励申请和发放
    """
    class Status(models.TextChoices):
        APPLIED = 'applied', _('已申请')
        APPROVED = 'approved', _('已批准')
        REJECTED = 'rejected', _('已拒绝')
        GRANTED = 'granted', _('已发放')
    
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='incentives',
        verbose_name=_('创作者')
    )
    period = models.CharField(
        _('统计周期'),
        max_length=50,
        help_text='如: 2024-01, 2024-Q1 等'
    )
    
    # 统计数据
    exposure = models.IntegerField(
        _('曝光量'),
        default=0,
        help_text='内容的总曝光次数'
    )
    likes = models.IntegerField(
        _('点赞数'),
        default=0
    )
    comments = models.IntegerField(
        _('评论数'),
        default=0
    )
    
    # 激励金额（可选）
    amount = models.DecimalField(
        _('激励金额'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    status = models.CharField(
        _('状态'),
        max_length=20,
        choices=Status.choices,
        default=Status.APPLIED,
        db_index=True
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_incentives',
        verbose_name=_('审核人')
    )
    review_note = models.TextField(
        _('审核备注'),
        blank=True,
        default=''
    )
    created_at = models.DateTimeField(
        _('申请时间'),
        auto_now_add=True,
        db_index=True
    )
    reviewed_at = models.DateTimeField(
        _('审核时间'),
        null=True,
        blank=True
    )
    granted_at = models.DateTimeField(
        _('发放时间'),
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'incentives'
        verbose_name = _('创作者激励')
        verbose_name_plural = _('创作者激励')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['author', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['period']),
        ]
    
    def __str__(self):
        return f"{self.author.username} - {self.period} ({self.get_status_display()})"

