"""api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # OAuth authentication
    path('api/auth/', include('drf_social_oauth2.urls', namespace='drf')),
    
    # Dashboard API - Requires Bearer token
    # Routes: /api/dashboard/sites/, /api/dashboard/projects/, /api/dashboard/experiences/, /api/dashboard/social-links/, /api/dashboard/api-keys/
    path('api/dashboard/', include('portfolios.urls')),
    path('api/dashboard/', include('projects.urls')),
    path('api/dashboard/', include('experiences.urls')),
    path('api/dashboard/', include('core.urls')),
    
    # Site API - Domain-based, public read
    # Routes: /api/sites/, /api/sites/projects/, /api/sites/projects/<slug>/
    path('api/public/', include('portfolios.api.public_urls')),
    path('api/public/', include('projects.api.public_urls')),
    
    # External API - Requires API key/secret
    # Routes: /v1/projects/, /v1/experiences/, /v1/social-links/
    path('v1/', include('projects.api.external_urls')),
    path('v1/', include('experiences.api.external_urls')),
]
