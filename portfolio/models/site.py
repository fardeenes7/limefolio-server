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


