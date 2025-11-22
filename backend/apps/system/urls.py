"""
System URLs
"""
from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'config', views.SysConfigViewSet, basename='sys-config')
router.register(r'logs', views.SysLogViewSet, basename='sys-log')
router.register(r'backup', views.BackupJobViewSet, basename='backup-job')
router.register(r'health', views.SystemHealthViewSet, basename='system-health')

urlpatterns = router.urls

