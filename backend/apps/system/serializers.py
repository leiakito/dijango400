"""
System serializers
"""
from rest_framework import serializers
from .models import SysLog, SysConfig, BackupJob, Incentive
from apps.users.serializers import UserProfileSerializer


class SysLogSerializer(serializers.ModelSerializer):
    """
    系统日志序列化器
    """
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = SysLog
        fields = [
            'id', 'level', 'module', 'message', 'context',
            'user', 'user_name', 'ip_address', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class SysConfigSerializer(serializers.ModelSerializer):
    """
    系统配置序列化器
    """
    class Meta:
        model = SysConfig
        fields = ['id', 'key', 'value', 'description', 'is_public', 'updated_at']
        read_only_fields = ['id', 'updated_at']


class BackupJobSerializer(serializers.ModelSerializer):
    """
    备份任务序列化器
    """
    duration = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()
    
    class Meta:
        model = BackupJob
        fields = [
            'id', 'status', 'file_path', 'file_name', 'file_size', 
            'error_message', 'started_at', 'finished_at', 'duration'
        ]
        read_only_fields = ['id', 'started_at']
    
    def get_duration(self, obj):
        return obj.duration
    
    def get_file_name(self, obj):
        """返回文件名（跨平台兼容）"""
        if obj.file_path:
            import os
            return os.path.basename(obj.file_path)
        return None


class IncentiveSerializer(serializers.ModelSerializer):
    """
    创作者激励序列化器
    """
    author = UserProfileSerializer(read_only=True)
    reviewer = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = Incentive
        fields = [
            'id', 'author', 'period', 'exposure', 'likes', 'comments',
            'amount', 'status', 'reviewer', 'review_note',
            'created_at', 'reviewed_at', 'granted_at'
        ]
        read_only_fields = [
            'id', 'author', 'status', 'reviewer', 
            'created_at', 'reviewed_at', 'granted_at'
        ]


class IncentiveApplySerializer(serializers.ModelSerializer):
    """
    激励申请序列化器
    """
    class Meta:
        model = Incentive
        fields = ['period', 'exposure', 'likes', 'comments']

