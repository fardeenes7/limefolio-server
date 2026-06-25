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
    
    # Status
    is_published = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    available_for_hire = models.BooleanField(default=False)

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
    
    # Cloudflare Custom Hostname ID
    cloudflare_id = models.CharField(max_length=255, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.domain} ({'verified' if self.status == 'verified' else 'pending'})"


class PortfolioTemplateConfig(models.Model):
    """
    Stores the user's sparse template customization deltas for their portfolio site.

    Design principle: only store what the user has explicitly changed from the
    template defaults. The full resolved config is computed at SSR time by merging
    these deltas with the static template definition in the Next.js codebase.
    Never store the resolved/merged result here.

    Fields:
        site             -- OneToOne link to the owning Site
        template_key     -- which template is active (must exist in the TS template registry)
        theme_key        -- active color theme (must exist in the TS theme registry)
        font_key         -- active font (must exist in the TS font registry)
        template_version -- semver of the template at the time of last save; used to
                           detect stale configs when a template is updated (Option C)
        config_overrides -- sparse dict of user variant/input overrides, keyed by
                           instanceId. Shape: { layout: {}, pages: { [pageKey]: {} } }
        config_additions -- user-added SectionInstance objects (repeatable components).
                           Shape: { layout: [], pages: { [pageKey]: [] } }
        config_removals  -- instanceIds the user has removed.
                           Shape: { layout: [], pages: { [pageKey]: [] } }
        config_ordering  -- user's preferred section order as instanceId arrays.
                           Shape: { layout: [], pages: { [pageKey]: [] } }
                           Sections not present in the array are appended in template order.
    """

    site = models.OneToOneField(
        'Site',
        on_delete=models.CASCADE,
        related_name='template_config',
    )
    template_key = models.CharField(max_length=100, default='default')
    theme_key = models.CharField(max_length=100, default='default')
    font_key = models.CharField(max_length=100, default='inter')
    template_version = models.CharField(max_length=20, default='1.0.0')

    # Sparse delta fields — never store the full merged result here
    config_overrides = models.JSONField(default=dict, blank=True)
    config_additions = models.JSONField(default=dict, blank=True)
    config_removals  = models.JSONField(default=dict, blank=True)
    config_ordering  = models.JSONField(default=dict, blank=True)
    theme_overrides  = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Portfolio Template Config'
        verbose_name_plural = 'Portfolio Template Configs'

    def __str__(self):
        return f'{self.site} — {self.template_key} v{self.template_version}'


class TemplateVersionMigrationLog(models.Model):
    """
    Audit log for template version migrations applied to a user's PortfolioTemplateConfig.

    When a template is updated in a breaking way (sections removed, instanceIds renamed,
    input keys changed), a Django management command queries all PortfolioTemplateConfig
    records on the old version, applies the migration, bumps template_version, and writes
    a record here.

    Fields:
        config          -- the PortfolioTemplateConfig that was migrated
        template_key    -- which template was migrated
        from_version    -- semver before migration
        to_version      -- semver after migration
        changes_applied -- human-readable or structured description of what was changed
                          (e.g. removed instanceIds, renamed keys, added new defaults)
        migrated_at     -- when the migration ran
        migrated_by     -- "auto" for management command, or staff user email for manual
    """

    config = models.ForeignKey(
        PortfolioTemplateConfig,
        on_delete=models.CASCADE,
        related_name='migration_logs',
    )
    template_key    = models.CharField(max_length=100)
    from_version    = models.CharField(max_length=20)
    to_version      = models.CharField(max_length=20)
    changes_applied = models.JSONField(default=list)   # list of change description strings
    migrated_at     = models.DateTimeField(auto_now_add=True)
    migrated_by     = models.CharField(max_length=255, default='auto')

    class Meta:
        ordering = ['-migrated_at']
        verbose_name = 'Template Version Migration Log'
        verbose_name_plural = 'Template Version Migration Logs'

    def __str__(self):
        return (
            f'{self.config.site} | {self.template_key} '
            f'{self.from_version} → {self.to_version}'
        )

class SiteSEO(models.Model):
    """SEO configuration for a Site, including global defaults and per-page overrides."""
    
    site = models.OneToOneField('Site', on_delete=models.CASCADE, related_name='seo')

    # Global defaults
    default_meta_title = models.CharField(max_length=60, blank=True)
    default_meta_description = models.TextField(max_length=160, blank=True)
    og_image = models.ImageField(upload_to='site_og/', blank=True, null=True)

    # Analytics & Tracking
    google_analytics_id = models.CharField(max_length=50, blank=True)
    google_tag_manager_id = models.CharField(max_length=50, blank=True)
    facebook_pixel_id = models.CharField(max_length=50, blank=True)

    # Robots / Crawling
    ROBOTS_CHOICES = [
        ('index,follow', 'Index, Follow (default)'),
        ('noindex,follow', 'No Index, Follow'),
        ('index,nofollow', 'Index, No Follow'),
        ('noindex,nofollow', 'No Index, No Follow'),
    ]
    robots_default = models.CharField(max_length=30, choices=ROBOTS_CHOICES, default='index,follow')

    # Per-page overrides (sparse dict of pageKey -> {meta_title, meta_description, og_image, robots})
    page_meta = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Site SEO'
        verbose_name_plural = 'Site SEOs'

    def __str__(self):
        return f'SEO config for {self.site}'
