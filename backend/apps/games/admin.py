"""
Game admin
"""
from django.contrib import admin
from .models import Publisher, Tag, Game, GameScreenshot, Collection, SinglePlayerRanking


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_info', 'website', 'created_at']
    search_fields = ['name', 'description']
    list_filter = ['created_at']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name', 'description']


class GameScreenshotInline(admin.TabularInline):
    """游戏截图内联编辑"""
    model = GameScreenshot
    extra = 1
    fields = ['image', 'title', 'description', 'order']
    ordering = ['order']


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'publisher', 'rating', 'download_count', 'heat_total', 'release_date']
    search_fields = ['name', 'description']
    list_filter = ['category', 'publisher', 'release_date', 'created_at']
    filter_horizontal = ['tags']
    readonly_fields = ['rating', 'download_count', 'follow_count', 'review_count', 
                       'heat_static', 'heat_dynamic', 'heat_total']
    inlines = [GameScreenshotInline]


@admin.register(GameScreenshot)
class GameScreenshotAdmin(admin.ModelAdmin):
    list_display = ['game', 'title', 'order', 'created_at']
    search_fields = ['game__name', 'title', 'description']
    list_filter = ['game', 'created_at']
    ordering = ['game', 'order']


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['user', 'game', 'created_at']
    search_fields = ['user__username', 'game__name']
    list_filter = ['created_at']


@admin.register(SinglePlayerRanking)
class SinglePlayerRankingAdmin(admin.ModelAdmin):
    list_display = ['source', 'rank', 'name', 'english_name', 'score', 'rating_count', 'fetched_at']
    search_fields = ['name', 'english_name', 'developer', 'publisher_name']
    list_filter = ['source', 'fetched_at']
    ordering = ['source', 'rank']
