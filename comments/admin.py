from django.contrib import admin
from .models import Page, Comment


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('title', 'content')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'page', 'get_comment_preview', 'parent', 'created_at']
    list_filter = ['created_at', 'page', 'parent']
    search_fields = ['content', 'author__username', 'page__title']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_comment_preview(self, obj):
        """Show first 50 characters of comment content"""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    get_comment_preview.short_description = 'Comment Preview'
    
    fieldsets = (
        (None, {
            'fields': ('page', 'author', 'parent', 'content')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )