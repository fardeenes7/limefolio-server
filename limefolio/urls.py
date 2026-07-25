"""api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from core.views import health_check
from public_api.views import DomainAskView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Caddy On-Demand TLS endpoint
    path('domains/ask', DomainAskView.as_view(), name='domain_ask'),
    
    # Health check
    path('health/', health_check, name='health_check'),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # OAuth authentication
    path('api/auth/', include('drf_social_oauth2.urls', namespace='drf')),
    # path('api/auth/custom-convert-token/', ConvertTokenView.as_view(), name='convert_token'),
    
    # Dashboard API - Requires Bearer token
    # Routes: /api/dashboard/site/, /api/dashboard/projects/, /api/dashboard/experiences/, /api/dashboard/social-links/, /api/dashboard/api-keys/, /api/dashboard/blog/, /api/dashboard/media/
    path('api/dashboard/', include('portfolios.urls')),
    path('api/dashboard/', include('projects.urls')),
    path('api/dashboard/', include('experiences.urls')),
    path('api/dashboard/', include('core.urls')),
    path('api/dashboard/', include('media.urls')),
    path('api/dashboard/blog/', include('blog.urls')),
    path('api/analytics/', include('analytics.urls')),
    path('api/billing/', include('billing.urls')),

    
    # Site API - Domain-based, public read
    # Routes: /api/public/sites/, /api/public/projects/, /api/public/experiences/, /api/public/skills/, /api/public/social-links/, /api/public/blog/, /api/public/media/
    path('api/public/', include('portfolios.api.public_urls')),
    path('api/public/', include('projects.api.public_urls')),
    path('api/public/', include('experiences.api.public_urls')),
    path('api/public/', include('blog.api.public_urls')),
    path('api/public/', include('media.api.public_urls')),
    path('api/public/migrate/', include('public_api.urls')),

    
    # External API - Requires API key/secret
    # Routes: /v1/projects/, /v1/experiences/, /v1/social-links/
    path('v1/', include('projects.api.external_urls')),
    path('v1/', include('experiences.api.external_urls')),
]
