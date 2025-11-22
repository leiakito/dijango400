"""
User serializers
"""
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User, UserOperation


class UserSerializer(serializers.ModelSerializer):
    """
    用户序列化器
    """
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'phone', 'role', 'status',
            'avatar', 'bio', 'register_time', 'last_login_time',
            'password'
        ]
        read_only_fields = ['id', 'register_time', 'last_login_time']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': False},
            'phone': {'required': False},
        }
    
    def create(self, validated_data):
        """创建用户时加密密码"""
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """更新用户时加密密码"""
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        return super().update(instance, validated_data)


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    用户注册序列化器
    """
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'password', 'password_confirm', 'role']
        extra_kwargs = {
            'email': {'required': False},
            'phone': {'required': False},
        }
    
    def validate(self, attrs):
        """验证密码一致性"""
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({'password': '两次输入的密码不一致'})
        attrs.pop('password_confirm')
        return attrs
    
    def create(self, validated_data):
        """创建用户"""
        validated_data['password'] = make_password(validated_data['password'])
        return User.objects.create(**validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    """
    用户个人资料序列化器（简化版）
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'avatar', 'bio', 'role']
        read_only_fields = ['id', 'username', 'role']


class CurrentUserSerializer(serializers.ModelSerializer):
    """
    当前登录用户序列化器
    允许用户更新基础资料与联系方式，限制角色/状态字段
    """
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'phone',
            'role', 'status', 'avatar', 'bio',
            'register_time', 'last_login_time'
        ]
        read_only_fields = ['id', 'role', 'status', 'register_time', 'last_login_time']


class UserOperationSerializer(serializers.ModelSerializer):
    """
    用户操作记录序列化器
    """
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UserOperation
        fields = ['id', 'user', 'user_name', 'content', 'ip_address', 'user_agent', 'created_at']
        read_only_fields = ['id', 'created_at']
