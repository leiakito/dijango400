"""
Community URLs
"""
from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'posts', views.PostViewSet, basename='post')
router.register(r'comments', views.CommentViewSet, basename='comment')
router.register(r'topics', views.TopicViewSet, basename='topic')
router.register(r'reactions', views.ReactionViewSet, basename='reaction')
router.register(r'reports', views.ReportViewSet, basename='report')
router.register(r'feedback', views.FeedbackViewSet, basename='feedback')

urlpatterns = router.urls
