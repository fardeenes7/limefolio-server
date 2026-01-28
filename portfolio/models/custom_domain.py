from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

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
