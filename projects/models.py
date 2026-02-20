
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.contrib.contenttypes.fields import GenericRelation

User = get_user_model()

class Project(models.Model):
    """Portfolio projects"""
    site = models.ForeignKey('portfolios.Site', on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=200)
    tagline = models.CharField(max_length=500, blank=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField()
    content = models.TextField(blank=True)

    # Media - using GenericRelation to the shared Media model
    media = GenericRelation('media.Media', related_query_name='project')
    
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

    @property
    def thumbnail(self):
        """Get the featured or first image as thumbnail"""
        try:
            if self.media.exists():
                # Get featured image first
                featured_media = self.media.filter(is_featured=True, image__isnull=False).first()
                if featured_media:
                    return featured_media.thumbnail.url if featured_media.thumbnail else featured_media.image.url
            
            # Fall back to first image
            first_media = self.media.filter(image__isnull=False).first()
            if first_media:
                return first_media.thumbnail.url if first_media.thumbnail else first_media.image.url
            
            # If no images, return None
            return None
        except Exception as e:
            print(f"Error getting thumbnail: {e}")        
        return None
