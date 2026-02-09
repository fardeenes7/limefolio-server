import re
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from uuid import uuid4

User = get_user_model()


# list of some common domains which are not allowed to be used as subdomain and maybe used by the system for other purposes
RESERVED_SUBDOMAINS = [
    # Core / DNS / Web defaults
    'www','root','home','index','default','site','main',
    # App & Platform
    'app','apps','client','ui','web','portal','dashboard','panel','console',
    # API & Services
    'api','apis','backend','server','services','service',
    'proxy','gateway','internal','private',
    # Documentation & Support
    'docs','doc','documentation','help','support','faq',
    'status','changelog','blog','news',
    # Authentication & Security
    'auth','login','logout','signup','signin','sso',
    'account','accounts','security','admin','administrator','sys','system',
    # Email & Communication
    'mail','email','smtp','imap','pop','webmail',
    'newsletter','notify','notifications',
    # Development & Testing
    'dev','development','test','testing','stage','staging',
    'preview','sandbox','beta','alpha','demo',
    # Assets & Storage
    'static','assets','cdn','media','files','uploads',
    'storage','images','img',
    # Analytics & Monitoring
    'analytics','stats','metrics','monitor','monitoring',
    'logs','logging','insights',
    # System & Infrastructure
    'limefolio','platform','common','core','global','shared',
    # Tools & Utilities
    'cli','sdk','webhook','hooks','events','cron',
    'jobs','worker','workers','queue',
    # Business & Finance
    'secure','payment','billing','invoice','payments','checkout'
]



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
    theme = models.CharField(max_length=50, default='default')
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(max_length=500, blank=True)
    
    # Status
    is_published = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    theme = models.CharField(max_length=50, default='default')
    template = models.CharField(max_length=50, default='default')
    font = models.CharField(max_length=50, default='inter')
    
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
    
    def clean(self):
        """Validate the model before saving"""
        from django.core.exceptions import ValidationError
        
        # Check if subdomain is reserved
        if self.subdomain and self.subdomain.lower() in RESERVED_SUBDOMAINS:
            raise ValidationError({
                'subdomain': f"Subdomain '{self.subdomain}' is reserved and cannot be used."
            })
    
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
        
        # Run model validation
        self.full_clean()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title





class CustomDomain(models.Model):
    """Custom domain mapping for portfolio sites"""
    STATUS_CHOICES = [
        ('pending', 'Pending Verification'),
        ('verified', 'Verified'),
        ('failed', 'Verification Failed'),
    ]
    
    site = models.ForeignKey('Site', on_delete=models.CASCADE, related_name='custom_domains')
    domain = models.CharField(max_length=253, unique=True, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # DNS verification
    verification_token = models.CharField(max_length=64, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.domain} ({'verified' if self.status == 'verified' else 'pending'})"
