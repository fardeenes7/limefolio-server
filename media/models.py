from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_delete
from django.dispatch import receiver
import uuid
import os


def media_file_upload_to(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{instance.uuid}.{ext}"
    return os.path.join('media', instance.content_type.model, filename)


class Media(models.Model):
    """Reusable media model for projects, blog posts, etc."""
    
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    # Generic relation to allow attachment to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Media files
    image = models.ImageField(upload_to=media_file_upload_to, blank=True, null=True)
    video = models.FileField(upload_to=media_file_upload_to, blank=True, null=True)
    thumbnail = models.ImageField(upload_to=media_file_upload_to, blank=True, null=True)
    
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
        media_type = self.media_type
        return f"{media_type.capitalize()} - {self.alt or self.uuid}"
    
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
        return 'unknown'
    
    @property
    def url(self):
        """Return the URL of the media"""
        if self.image:
            return self.image.url
        elif self.video:
            return self.video.url
        return None

@receiver(post_delete, sender=Media)
def delete_media_files(sender, instance, **kwargs):
    """Delete files from S3/storage when Media object is deleted"""
    if instance.image:
        instance.image.delete(save=False)
    if instance.video:
        instance.video.delete(save=False)
    if instance.thumbnail:
        instance.thumbnail.delete(save=False)
