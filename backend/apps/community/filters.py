"""
Community filters
"""
import django_filters
from .models import Post, Topic


class PostFilter(django_filters.FilterSet):
    """
    动态过滤器
    """
    author = django_filters.NumberFilter(field_name='author__id')
    game = django_filters.NumberFilter(field_name='game__id')
    topic = django_filters.NumberFilter(field_name='topics__id')
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = Post
        fields = ['author', 'game', 'topic']


class TopicFilter(django_filters.FilterSet):
    """
    话题过滤器
    """
    name = django_filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = Topic
        fields = ['name']

