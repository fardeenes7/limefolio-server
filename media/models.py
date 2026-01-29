from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Media(models.Model):
    """Reusable media model for projects, blog posts, etc."""
    
    # Generic relation to allow attachment to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Media files
    image = models.ImageField(upload_to='media/%Y/%m/', blank=True, null=True)
    video = models.FileField(upload_to='media/%Y/%m/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='media/thumbnails/%Y/%m/', blank=True, null=True)
    
    # Metadata
    alt = models.CharField(max_length=200, blank=True, help_text='Alternative text for accessibility')
    caption = models.TextField(blank=True, help_text='Media caption or description')
    
    # Display options
    order = models.PositiveIntegerField(default=0, help_text='Display order')
    is_featured = models.BooleanField(default=False, help_text='Featured/primary media')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', '-created_at']
        verbose_name_plural = 'Media'
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['order']),
        ]
    
    def clean(self):
        """Ensure at least one media type is provided"""
        if not self.image and not self.video:
            raise ValidationError('Either image or video must be provided.')
    
    def __str__(self):
        media_type = self.media_type()
        return f"{media_type.capitalize()} - {self.alt or self.id}"
    
    def save(self, *args, **kwargs):
        # Auto-generate alt text from filename if not provided
        if not self.alt:
            if self.image:
                self.alt = self.image.name.split('/')[-1]
            elif self.video:
                self.alt = self.video.name.split('/')[-1]
        super().save(*args, **kwargs)
    
    @property
    def media_type(self):
        """Return the type of media"""
        if self.image:
            return 'image'
        elif self.video:
            return 'video'
        return None
    
    @property
    def url(self):
        """Return the URL of the media"""
        if self.image:
            return self.image.url
        elif self.video:
            return self.video.url
        return None
