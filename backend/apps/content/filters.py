"""
Content filters
"""
import django_filters
from .models import Strategy


class StrategyFilter(django_filters.FilterSet):
    """
    攻略过滤器
    """
    title = django_filters.CharFilter(lookup_expr='icontains')
    game = django_filters.NumberFilter(field_name='game__id')
    author = django_filters.NumberFilter(field_name='author__id')
    status = django_filters.ChoiceFilter(choices=Strategy.Status.choices)
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = Strategy
        fields = ['title', 'game', 'author', 'status']

