"""
Games filters
"""
import django_filters
from .models import Game


class GameFilter(django_filters.FilterSet):
    """
    游戏过滤器
    """
    name = django_filters.CharFilter(lookup_expr='icontains')
    category = django_filters.CharFilter(lookup_expr='icontains')
    publisher = django_filters.NumberFilter(field_name='publisher__id')
    tags = django_filters.CharFilter(method='filter_tags')
    release_date_after = django_filters.DateFilter(field_name='release_date', lookup_expr='gte')
    release_date_before = django_filters.DateFilter(field_name='release_date', lookup_expr='lte')
    min_rating = django_filters.NumberFilter(field_name='rating', lookup_expr='gte')
    
    class Meta:
        model = Game
        fields = ['name', 'category', 'publisher', 'tags']
    
    def filter_tags(self, queryset, name, value):
        """按标签ID列表筛选（逗号分隔）"""
        if value:
            tag_ids = [int(id.strip()) for id in value.split(',') if id.strip().isdigit()]
            if tag_ids:
                for tag_id in tag_ids:
                    queryset = queryset.filter(tags__id=tag_id)
        return queryset

