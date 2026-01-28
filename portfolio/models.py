import re
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.text import slugify
from uuid import uuid4

User = get_user_model()


class Site(models.Model):
    """User's portfolio site"""
    
    # Subdomain validator: lowercase letters, numbers, hyphens (DNS-compliant)
    subdomain_validator = RegexValidator(
        regex=r'^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$',
        message='Subdomain must contain only lowercase letters, numbers, and hyphens. '
                'Must start and end with alphanumeric character.',
        code='invalid_subdomain'
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='site')
    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)
    subdomain = models.SlugField(
        max_length=63, 
        unique=True, 
        db_index=True,
        validators=[subdomain_validator],
        help_text='Unique subdomain for your portfolio (e.g., yourname.limefolio.com)'
    )
    title = models.CharField(max_length=200)
    tagline = models.CharField(max_length=500, blank=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='site_logos/', blank=True, null=True)
    favicon = models.ImageField(upload_to='site_favicons/', blank=True, null=True)
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(max_length=500, blank=True)
    
    # Status
    is_published = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def _sanitize_subdomain(self, value):
        """Sanitize username to create valid subdomain"""
        # Convert to lowercase and replace underscores with hyphens
        sanitized = value.lower().replace('_', '-')
        
        # Remove any characters that aren't alphanumeric or hyphen
        sanitized = re.sub(r'[^a-z0-9-]', '', sanitized)
        
        # Remove leading/trailing hyphens
        sanitized = sanitized.strip('-')
        
        # Ensure it starts with alphanumeric (remove leading hyphens)
        sanitized = re.sub(r'^-+', '', sanitized)
        
        # Ensure it ends with alphanumeric (remove trailing hyphens)
        sanitized = re.sub(r'-+$', '', sanitized)
        
        # Collapse multiple consecutive hyphens
        sanitized = re.sub(r'-+', '-', sanitized)
        
        # Truncate to max 63 characters
        sanitized = sanitized[:63]
        
        # If empty after sanitization, use a default
        if not sanitized:
            sanitized = f'user-{self.user.id}'
        
        return sanitized
    
    def save(self, *args, **kwargs):
        # Auto-populate subdomain from username if not provided
        if not self.subdomain:
            base_subdomain = self._sanitize_subdomain(self.user.username)
            subdomain = base_subdomain
            
            # Handle uniqueness by appending number if needed
            counter = 1
            while Site.objects.filter(subdomain=subdomain).exclude(pk=self.pk).exists():
                subdomain = f"{base_subdomain}-{counter}"
                counter += 1
            
            self.subdomain = subdomain
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title


class CustomDomain(models.Model):
    """Custom domains for sites"""
    STATUS_CHOICES = [
        ('pending', 'Pending Verification'),
        ('verified', 'Verified'),
        ('failed', 'Verification Failed'),
    ]
    
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='custom_domains')
    domain = models.CharField(max_length=255, unique=True, db_index=True)
    is_primary = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # DNS verification
    verified_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_primary', '-created_at']
        unique_together = [['site', 'domain']]
    
    def __str__(self):
        return self.domain


class Project(models.Model):
    """Portfolio projects"""
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='projects')
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


class Experience(models.Model):
    """Work experience entries"""
    TYPE_CHOICES = [
        ('Full Time', 'Full Time'),
        ('Part Time', 'Part Time'),
        ('Internship', 'Internship'),
        ('Freelance', 'Freelance'),
    ]
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='experiences')
    company = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='Full Time', blank=True)
    
    company_logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    
    order = models.PositiveIntegerField(default=0)

    is_published = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_current', '-start_date', 'order']
    
    def __str__(self):
        return f"{self.position} at {self.company}"


class SocialLink(models.Model):
    """Social media links"""
    PLATFORMS = [
        ('github', 'GitHub'),
        ('linkedin', 'LinkedIn'),
        ('twitter', 'Twitter'),
        ('instagram', 'Instagram'),
        ('facebook', 'Facebook'),
        ('youtube', 'YouTube'),
        ('dribbble', 'Dribbble'),
        ('behance', 'Behance'),
        ('medium', 'Medium'),
        ('dev', 'Dev.to'),
        ('stackoverflow', 'Stack Overflow'),
        ('other', 'Other'),
    ]
    
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='social_links')
    platform = models.CharField(max_length=20, choices=PLATFORMS)
    url = models.URLField()
    username = models.CharField(max_length=100, blank=True)
    
    order = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'platform']
    
    def __str__(self):
        return f"{self.platform} - {self.site.user.username}"
