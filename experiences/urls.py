"""
URL configuration for experiences app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from experiences.views import (
    DashboardExperienceViewSet, DashboardSocialLinkViewSet,
    ExternalExperienceViewSet, ExternalSocialLinkViewSet
)

# Dashboard router
dashboard_router = DefaultRouter()
dashboard_router.register(r'experiences', DashboardExperienceViewSet, basename='dashboard-experiences')
dashboard_router.register(r'social-links', DashboardSocialLinkViewSet, basename='dashboard-social-links')

# External router
external_router = DefaultRouter()
external_router.register(r'experiences', ExternalExperienceViewSet, basename='external-experiences')
external_router.register(r'social-links', ExternalSocialLinkViewSet, basename='external-social-links')

# URL patterns
urlpatterns = [
    # Dashboard URLs
    path('dashboard/', include(dashboard_router.urls)),
    
    # External API URLs
    path('external/', include(external_router.urls)),
]
