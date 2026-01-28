"""
External API URLs - Requires API Key/Secret
For third-party integrations and programmatic access
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExternalProjectViewSet, ExternalExperienceViewSet, ExternalSocialLinkViewSet

router = DefaultRouter()
router.register(r'projects', ExternalProjectViewSet, basename='external-projects')
router.register(r'experiences', ExternalExperienceViewSet, basename='external-experiences')
router.register(r'social-links', ExternalSocialLinkViewSet, basename='external-social-links')

urlpatterns = [
    path('', include(router.urls)),
]