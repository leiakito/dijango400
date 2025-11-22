"""
自定义JWT认证类
仅包含认证逻辑，避免循环导入
"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from django.utils.translation import gettext_lazy as _


class CustomJWTAuthentication(JWTAuthentication):
    """
    自定义JWT认证，增加用户状态检查
    """
    
    def authenticate(self, request):
        """
        重写认证方法，在JWT验证后检查用户状态
        """
        # 调用父类方法进行JWT验证
        result = super().authenticate(request)
        
        if result is None:
            return None
        
        user, validated_token = result
        
        # 动态导入User模型，避免循环导入
        from apps.users.models import User
        
        # 检查用户状态
        if user.status == User.Status.BANNED:
            raise AuthenticationFailed(
                _('该账户已被封禁，无法访问系统'),
                code='user_banned'
            )
        
        # 检查用户是否激活
        if not user.is_active:
            raise AuthenticationFailed(
                _('该账户未激活'),
                code='user_inactive'
            )
        
        return user, validated_token

