"""
User models - 用户与RBAC
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    自定义用户模型
    扩展 Django 默认用户，添加角色、状态等字段
    """
    class Role(models.TextChoices):
        PLAYER = 'player', _('普通玩家')
        CREATOR = 'creator', _('内容创作者')
        PUBLISHER = 'publisher', _('发行商')
        ADMIN = 'admin', _('系统管理员')
    
    class Status(models.IntegerChoices):
        BANNED = 0, _('封禁')
        NORMAL = 1, _('正常')
    
    # 基础字段（继承自 AbstractUser: username, first_name, last_name, email, password, etc.）
    phone = models.CharField(
        _('手机号'),
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        db_index=True
    )
    role = models.CharField(
        _('角色'),
        max_length=20,
        choices=Role.choices,
        default=Role.PLAYER,
        db_index=True
    )
    status = models.IntegerField(
        _('状态'),
        choices=Status.choices,
        default=Status.NORMAL,
        db_index=True
    )
    register_time = models.DateTimeField(
        _('注册时间'),
        auto_now_add=True
    )
    last_login_time = models.DateTimeField(
        _('最后登录时间'),
        null=True,
        blank=True
    )
    avatar = models.ImageField(
        _('头像'),
        upload_to='avatars/%Y/%m/',
        null=True,
        blank=True
    )
    bio = models.TextField(
        _('个人简介'),
        max_length=500,
        blank=True,
        default=''
    )
    
    class Meta:
        db_table = 'users'
        verbose_name = _('用户')
        verbose_name_plural = _('用户')
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['role']),
            models.Index(fields=['status']),
            models.Index(fields=['-register_time']),
        ]
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def is_player(self):
        return self.role == self.Role.PLAYER
    
    def is_creator(self):
        return self.role == self.Role.CREATOR
    
    def is_publisher(self):
        return self.role == self.Role.PUBLISHER
    
    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser
    
    def is_active_user(self):
        return self.status == self.Status.NORMAL


class UserOperation(models.Model):
    """
    用户操作记录
    记录用户的重要操作行为
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='operations',
        verbose_name=_('用户')
    )
    content = models.TextField(
        _('操作内容'),
        help_text='操作的详细描述'
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
        _('创建时间'),
        auto_now_add=True,
        db_index=True
    )
    
    class Meta:
        db_table = 'user_operations'
        verbose_name = _('用户操作记录')
        verbose_name_plural = _('用户操作记录')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.content[:50]}"

