from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Experience(models.Model):
    """Work experience entries"""
    TYPE_CHOICES = [
        ('Full Time', 'Full Time'),
        ('Part Time', 'Part Time'),
        ('Internship', 'Internship'),
        ('Freelance', 'Freelance'),
    ]
    site = models.ForeignKey('Site', on_delete=models.CASCADE, related_name='experiences')
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


