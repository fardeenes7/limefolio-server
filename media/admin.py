from django.contrib import admin
from .models import Media


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ['id', 'media_type', 'alt', 'content_type', 'object_id', 'is_featured', 'order', 'created_at']
    list_filter = ['is_featured', 'content_type', 'created_at']
    search_fields = ['alt', 'caption']
    ordering = ['order', '-created_at']
    
    fieldsets = (
        ('Media Files', {
            'fields': ('image', 'video', 'thumbnail')
        }),
        ('Metadata', {
            'fields': ('alt', 'caption', 'order', 'is_featured')
        }),
        ('Content Relation', {
            'fields': ('content_type', 'object_id'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['content_type', 'object_id']
