"""
User URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, UserOperationViewSet

router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')
router.register(r'operations', UserOperationViewSet, basename='user-operation')

urlpatterns = router.urls

