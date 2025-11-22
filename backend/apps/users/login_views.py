"""
自定义登录视图
"""
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    自定义Token序列化器，在登录时检查用户状态
    """
    
    def validate(self, attrs):
        """
        在生成token前检查用户状态
        """
        # 先获取用户
        username = attrs.get(self.username_field)
        
        try:
            user = User.objects.get(username=username)
            
            # 检查用户状态
            if user.status == User.Status.BANNED:
                raise AuthenticationFailed(
                    '该账户已被封禁，无法登录',
                    code='user_banned'
                )
            
            # 检查用户是否激活
            if not user.is_active:
                raise AuthenticationFailed(
                    '该账户未激活',
                    code='user_inactive'
                )
        except User.DoesNotExist:
            pass  # 让父类处理用户不存在的情况
        
        # 调用父类方法生成token
        data = super().validate(attrs)
        
        # 登录成功，记录系统日志
        try:
            user = User.objects.get(username=username)
            now = timezone.now()
            # 更新最后登录时间
            User.objects.filter(pk=user.pk).update(
                last_login=now,
                last_login_time=now
            )
            from apps.system.middleware import log_system_event
            log_system_event(
                level='INFO',
                module='auth',
                message=f"用户登录: {username}",
                context={
                    'username': username,
                    'role': user.role,
                    'login_success': True
                },
                user=user
            )
        except Exception as e:
            # 日志记录失败不应该影响登录
            pass
        
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    自定义Token获取视图，使用自定义序列化器
    """
    serializer_class = CustomTokenObtainPairSerializer
