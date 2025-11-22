"""
通用权限类
"""
from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    仅管理员可访问
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin()


class IsPublisher(permissions.BasePermission):
    """
    仅发行商可访问
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_publisher()


class IsAdminOrPublisher(permissions.BasePermission):
    """
    管理员或发行商可访问
    """
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.is_admin() or request.user.is_publisher())
        )


class IsCreator(permissions.BasePermission):
    """
    仅内容创作者可访问
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_creator()


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    仅资源所有者或管理员可访问
    """
    def has_object_permission(self, request, view, obj):
        # 管理员有所有权限
        if request.user.is_admin():
            return True
        
        # 检查是否是资源所有者
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'author'):
            return obj.author == request.user
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
        
        return False


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    所有者可编辑，其他人只读
    """
    def has_object_permission(self, request, view, obj):
        # 读取权限允许所有人
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # 写入权限仅所有者或管理员
        if request.user.is_admin():
            return True
        
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'author'):
            return obj.author == request.user
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
        
        return False
