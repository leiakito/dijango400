"""
Content URLs
"""
from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'strategies', views.StrategyViewSet, basename='strategy')
router.register(r'review', views.ContentReviewViewSet, basename='content-review')
router.register(r'media', views.MediaAssetViewSet, basename='media')
router.register(r'incentives', views.IncentiveViewSet, basename='incentive')

urlpatterns = router.urls
