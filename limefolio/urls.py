"""api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # OAuth authentication
    path('api/auth/', include('drf_social_oauth2.urls', namespace='drf')),
    
    # Dashboard API - Requires Bearer token
    path('api/dashboard/site/', include('portfolios.urls')),
    path('api/dashboard/', include('projects.urls')),
    path('api/dashboard/', include('experiences.urls')),
    path('api/dashboard/api-keys/', include('core.urls')),
    
    # Site API - Domain-based, public read
    path('api/site/', include('portfolios.urls')),
    path('api/site/projects/', include('projects.urls')),
    
    # External API - Requires API key/secret
    path('v1/projects/', include('projects.urls')),
    path('v1/', include('experiences.urls')),
]
