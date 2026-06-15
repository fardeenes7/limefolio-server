from django.db import models
from django.utils.text import slugify
from django.contrib.contenttypes.fields import GenericRelation


class BlogPost(models.Model):
    """Blog posts for portfolio sites"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    site = models.ForeignKey('portfolios.Site', on_delete=models.CASCADE, related_name='blog_posts')
    
    # Content
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100, unique=True)
    excerpt = models.TextField(blank=True, help_text='Short description/summary')
    content = models.TextField(help_text='Full blog post content (supports Markdown)')
    
    # Media - using ManyToMany through the media app
    media = GenericRelation('media.Media', related_query_name='blog_post')
    thumbnail_url = models.URLField(max_length=500, blank=True, help_text='Direct URL to thumbnail image (overrides media thumbnail)')
    
    # Metadata
    author = models.CharField(max_length=100, blank=True, help_text='Author name override')
    tags = models.JSONField(default=list, blank=True, help_text='List of tags')
    categories = models.JSONField(default=list, blank=True, help_text='List of categories')
    
    # SEO
    meta_description = models.CharField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)
    
    # Publishing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    
    # Reading time (in minutes)
    reading_time = models.PositiveIntegerField(default=0, help_text='Estimated reading time in minutes')
    
    # Stats
    view_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-published_at', '-created_at']
        unique_together = [['site', 'slug']]
        indexes = [
            models.Index(fields=['-published_at']),
            models.Index(fields=['status']),
            models.Index(fields=['is_featured']),
        ]
    
    def __str__(self):
        return f"{self.site.user.username} - {self.title}"
    
    def save(self, *args, **kwargs):
        # Auto-generate slug if not provided
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Auto-generate excerpt from content if not provided
        if not self.excerpt and self.content:
            # Take first 200 characters
            self.excerpt = self.content[:200] + '...' if len(self.content) > 200 else self.content
        
        # Calculate reading time based on content
        if self.content:
            # Average reading speed: 200 words per minute
            word_count = len(self.content.split())
            self.reading_time = max(1, round(word_count / 200))
        
        super().save(*args, **kwargs)
    
    @property
    def thumbnail(self):
        """Get the featured or first image as thumbnail"""
        if self.thumbnail_url:
            return self.thumbnail_url
            
        featured_media = self.media.filter(is_featured=True, image__isnull=False).first()
        if featured_media:
            return featured_media.thumbnail.url if featured_media.thumbnail else featured_media.image.url
        
        first_media = self.media.filter(image__isnull=False).first()
        if first_media:
            return first_media.thumbnail.url if first_media.thumbnail else first_media.image.url
        
        return None
    
    @property
    def is_published(self):
        """Check if the post is published"""
        return self.status == 'published'


class BlogComment(models.Model):
    """Comments on blog posts (optional feature)"""
    
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    
    # Author info
    author_name = models.CharField(max_length=100)
    author_email = models.EmailField()
    author_website = models.URLField(blank=True)
    
    # Content
    content = models.TextField()
    
    # Moderation
    is_approved = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['post', '-created_at']),
            models.Index(fields=['is_approved']),
        ]
    
    def __str__(self):
        return f"{self.author_name} on {self.post.title}"
