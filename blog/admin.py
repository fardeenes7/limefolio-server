from django.contrib import admin
from .models import BlogPost, BlogComment


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'site', 'status', 'is_featured', 'published_at', 'view_count', 'created_at']
    list_filter = ['status', 'is_featured', 'published_at', 'created_at']
    search_fields = ['title', 'excerpt', 'content', 'tags', 'categories']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'
    ordering = ['-published_at', '-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('site', 'title', 'slug', 'excerpt', 'content')
        }),
        ('Author & Metadata', {
            'fields': ('author', 'tags', 'categories')
        }),
        ('SEO', {
            'fields': ('meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Publishing', {
            'fields': ('status', 'is_featured', 'published_at')
        }),
        ('Stats', {
            'fields': ('reading_time', 'view_count'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['reading_time', 'view_count']


@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ['author_name', 'post', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'created_at']
    search_fields = ['author_name', 'author_email', 'content']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Comment Information', {
            'fields': ('post', 'content')
        }),
        ('Author Details', {
            'fields': ('author_name', 'author_email', 'author_website')
        }),
        ('Moderation', {
            'fields': ('is_approved',)
        }),
    )
    
    actions = ['approve_comments', 'unapprove_comments']
    
    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, f"{queryset.count()} comments approved.")
    approve_comments.short_description = "Approve selected comments"
    
    def unapprove_comments(self, request, queryset):
        queryset.update(is_approved=False)
        self.message_user(request, f"{queryset.count()} comments unapproved.")
    unapprove_comments.short_description = "Unapprove selected comments"
