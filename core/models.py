import secrets
import hashlib
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class APIKey(models.Model):
    """API keys for external/programmatic access to portfolio data"""
    
    site = models.ForeignKey('portfolios.Site', on_delete=models.CASCADE, related_name='api_keys')
    name = models.CharField(max_length=200, help_text='Descriptive name for this API key')
    
    # Key and secret
    key = models.CharField(max_length=64, unique=True, db_index=True, editable=False)
    secret_hash = models.CharField(max_length=128, editable=False)  # Hashed secret
    
    # Permissions
    is_active = models.BooleanField(default=True)
    read_only = models.BooleanField(default=True, help_text='If true, only GET requests allowed')
    
    # Rate limiting
    rate_limit = models.IntegerField(
        default=1000, 
        help_text='Maximum requests per hour'
    )
    request_count = models.IntegerField(default=0)
    rate_limit_reset_at = models.DateTimeField(null=True, blank=True)
    
    # Tracking
    last_used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'API Key'
        verbose_name_plural = 'API Keys'
    
    def __str__(self):
        return f"{self.name} - {self.key[:16]}..."
    
    @staticmethod
    def generate_key():
        """Generate a random API key"""
        return f"lf_{''.join(secrets.token_urlsafe(32))}"[:64]
    
    @staticmethod
    def generate_secret():
        """Generate a random API secret"""
        return secrets.token_urlsafe(48)
    
    @staticmethod
    def hash_secret(secret):
        """Hash the API secret for storage"""
        return hashlib.sha256(secret.encode()).hexdigest()
    
    def verify_secret(self, secret):
        """Verify a secret against the stored hash"""
        return self.secret_hash == self.hash_secret(secret)
    
    def save(self, *args, **kwargs):
        # Generate key if not provided
        if not self.key:
            self.key = self.generate_key()
            # Ensure uniqueness
            while APIKey.objects.filter(key=self.key).exists():
                self.key = self.generate_key()
        
        super().save(*args, **kwargs)
    
    def increment_request_count(self):
        """Increment request count and check rate limit"""
        now = timezone.now()
        
        # Reset counter if hour has passed
        if not self.rate_limit_reset_at or now >= self.rate_limit_reset_at:
            self.request_count = 0
            self.rate_limit_reset_at = now + timezone.timedelta(hours=1)
        
        self.request_count += 1
        self.last_used_at = now
        self.save(update_fields=['request_count', 'rate_limit_reset_at', 'last_used_at'])
        
        return self.request_count <= self.rate_limit
    
    def is_rate_limited(self):
        """Check if API key has exceeded rate limit"""
        if not self.rate_limit_reset_at:
            return False
        
        now = timezone.now()
        if now >= self.rate_limit_reset_at:
            return False
        
        return self.request_count >= self.rate_limit
