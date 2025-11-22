"""
Recommendation URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'config', views.AlgoConfigViewSet, basename='algo-config')
router.register(r'metrics', views.GameMetricsDailyViewSet, basename='game-metrics')

urlpatterns = [
    path('hot/', views.hot_games, name='hot-games'),
    path('new/', views.new_games, name='new-games'),
    path('personal/', views.personal_recommendations, name='personal-recommendations'),
] + router.urls

