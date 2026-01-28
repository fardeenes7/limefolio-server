import re
import secrets
import hashlib
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.text import slugify
from django.utils import timezone
from uuid import uuid4

User = get_user_model()

class Project(models.Model):
    """Portfolio projects"""
    site = models.ForeignKey('Site', on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100)
    description = models.TextField()
    content = models.TextField(blank=True)

    
    # Links
    project_url = models.URLField(blank=True, null=True, help_text='Live project URL')
    github_url = models.URLField(blank=True, null=True, help_text='Source code URL')
    
    # Technologies
    technologies = models.JSONField(default=list, blank=True, help_text='List of technologies used')
    
    # Metadata
    featured = models.BooleanField(default=False)
    
    # Dates
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-featured', 'order', '-created_at']
        unique_together = [['site', 'slug']]
    
    def __str__(self):
        return f"{self.site.user.username} - {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def thumbnail_url(self):
        if self.media.exists():
            # Get the media which is image and not video, and is featured, if there is not featured image, get the first image
            featured_media = self.media.filter(is_featured=True, video__isnull=True).first()
            if featured_media:
                return featured_media.thumbnail.url
            return self.media.filter(video__isnull=True).first().thumbnail.url
        return None


class ProjectMedia(models.Model):
    """Media for portfolio projects"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='media')
    image = models.ImageField(upload_to='project_media/', blank=True, null=True)
    video = models.FileField(upload_to='project_media/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='project_media/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', '-created_at']
    
    def clean(self):
        """Ensure at least one media type is provided"""
        if not self.image and not self.video:
            raise ValidationError('Either image or video must be provided.')
    
    def __str__(self):
        return f"{self.project.title} - {self.order}"


