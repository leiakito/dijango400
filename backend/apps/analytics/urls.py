"""
Analytics URLs - 简化版，需要根据实际需求完善
"""
from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

urlpatterns = [
    path('overview/', views.overview, name='analytics-overview'),
    path('publisher/', views.publisher_overview, name='analytics-publisher'),
    path('heatmap/', views.heatmap, name='analytics-heatmap'),
] + router.urls
