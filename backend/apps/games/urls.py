"""
Game URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# 创建路由器
router = DefaultRouter()

# 注意: 空路径必须放在最后,否则会拦截所有请求
router.register(r'publishers', views.PublisherViewSet, basename='publisher')
router.register(r'tags', views.TagViewSet, basename='tag')
router.register(r'single-player-rankings', views.SinglePlayerRankingViewSet, basename='single-player-ranking')
router.register(r'', views.GameViewSet, basename='game')

urlpatterns = router.urls
