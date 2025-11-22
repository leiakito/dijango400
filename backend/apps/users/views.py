"""
User views
"""
from django.utils import timezone
from django.db.models import Count
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import User, UserOperation
from .serializers import (
    UserSerializer, UserRegisterSerializer, 
    UserProfileSerializer, CurrentUserSerializer, UserOperationSerializer
)
from config.permissions import IsAdmin, IsOwnerOrAdmin


class UserViewSet(viewsets.ModelViewSet):
    """
    用户管理视图集
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['role', 'status']
    search_fields = ['username', 'email']
    ordering_fields = ['register_time', 'last_login_time']
    ordering = ['-register_time']
    
    def get_permissions(self):
        """根据操作设置权限"""
        if self.action == 'create':
            return [permissions.AllowAny()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsOwnerOrAdmin()]
        elif self.action in ['list']:
            return [IsAdmin()]
        return [permissions.IsAuthenticated()]
    
    def get_serializer_class(self):
        """根据操作返回不同的序列化器"""
        if self.action == 'create':
            return UserRegisterSerializer
        elif self.action == 'me':
            return CurrentUserSerializer
        return UserSerializer
    
    @action(detail=False, methods=['get', 'patch'])
    def me(self, request):
        """
        获取或更新当前用户信息
        GET /api/v1/users/me/
        PATCH /api/v1/users/me/
        """
        user = request.user
        
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        
        elif request.method == 'PATCH':
            serializer = self.get_serializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='upload-avatar')
    def upload_avatar(self, request):
        """
        上传并更新当前用户头像
        POST /api/v1/users/upload-avatar/
        Body: multipart/form-data { avatar: <File> }
        """
        user = request.user
        avatar_file = request.FILES.get('avatar')

        if not avatar_file:
            return Response({'error': '未找到头像文件'}, status=status.HTTP_400_BAD_REQUEST)

        user.avatar = avatar_file
        user.save(update_fields=['avatar'])

        avatar_url = user.avatar.url if user.avatar else ''
        full_url = request.build_absolute_uri(avatar_url) if avatar_url else avatar_url

        return Response({
            'avatar': full_url or avatar_url,
            'message': '头像上传成功'
        })
    
    @action(detail=True, methods=['patch'], permission_classes=[IsAdmin])
    def status(self, request, pk=None):
        """
        修改用户状态（封禁/解封）
        PATCH /api/v1/users/{id}/status/
        Body: {"status": 0/1, "reason": "原因（可选）"}
        """
        user = self.get_object()
        new_status = request.data.get('status')
        reason = request.data.get('reason', '')
        
        if new_status not in [User.Status.NORMAL, User.Status.BANNED]:
            return Response(
                {'error': '无效的状态值'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        old_status = user.status
        user.status = new_status
        user.save(update_fields=['status'])
        
        # 记录操作
        operation_content = f"状态变更: {user.get_status_display()}"
        if reason:
            operation_content += f" - 原因: {reason}"
        
        UserOperation.objects.create(
            user=user,
            content=operation_content,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # 记录系统日志
        from apps.system.middleware import log_system_event
        log_level = 'WARNING' if new_status == User.Status.BANNED else 'INFO'
        log_system_event(
            level=log_level,
            module='user',
            message=f"管理员{'封禁' if new_status == User.Status.BANNED else '修改'}用户 {user.username} 状态",
            context={
                'user_id': user.id,
                'username': user.username,
                'old_status': old_status,
                'new_status': new_status,
                'reason': reason,
                'operator': request.user.username
            },
            user=request.user
        )
        
        return Response({
            'status': user.status,
            'status_display': user.get_status_display(),
            'message': '操作成功'
        })
    
    @action(detail=True, methods=['patch'], permission_classes=[IsAdmin])
    def role(self, request, pk=None):
        """
        修改用户角色
        PATCH /api/v1/users/{id}/role/
        Body: {"role": "player/creator/publisher/admin"}
        """
        user = self.get_object()
        new_role = request.data.get('role')
        
        if new_role not in [choice[0] for choice in User.Role.choices]:
            return Response(
                {'error': '无效的角色值'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        old_role = user.role
        user.role = new_role
        user.save(update_fields=['role'])
        
        # 记录操作
        UserOperation.objects.create(
            user=user,
            content=f"角色变更: {dict(User.Role.choices)[old_role]} -> {user.get_role_display()}",
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # 记录系统日志
        from apps.system.middleware import log_system_event
        log_system_event(
            level='INFO',
            module='user',
            message=f"管理员修改用户 {user.username} 角色",
            context={
                'user_id': user.id,
                'username': user.username,
                'old_role': old_role,
                'new_role': new_role,
                'operator': request.user.username
            },
            user=request.user
        )
        
        return Response({
            'role': user.role,
            'role_display': user.get_role_display(),
            'message': '角色更新成功'
        })
    
    @action(detail=True, methods=['get'], permission_classes=[IsAdmin])
    def operations(self, request, pk=None):
        """
        获取指定用户的操作记录
        GET /api/v1/users/{id}/operations/
        """
        user = self.get_object()
        operations = user.operations.all()[:50]  # 最近50条
        serializer = UserOperationSerializer(operations, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAdmin])
    def statistics(self, request):
        """
        获取用户统计信息
        GET /api/v1/users/statistics/
        """
        from datetime import timedelta
        
        total_users = User.objects.count()
        stats = {
            'total': total_users,
            'by_role': {},
            'by_status': {},
            'recent_registrations': User.objects.filter(
                register_time__gte=timezone.now() - timedelta(days=30)
            ).count()
        }
        
        # 按角色统计
        role_stats = User.objects.values('role').annotate(count=Count('id'))
        for item in role_stats:
            stats['by_role'][item['role']] = item['count']
        
        # 按状态统计
        status_stats = User.objects.values('status').annotate(count=Count('id'))
        for item in status_stats:
            stats['by_status'][item['status']] = item['count']
        
        return Response(stats)


class UserOperationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    用户操作记录视图集（只读）
    """
    queryset = UserOperation.objects.all()
    serializer_class = UserOperationSerializer
    permission_classes = [IsAdmin]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['user']
    ordering = ['-created_at']
