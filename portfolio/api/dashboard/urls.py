"""
Dashboard API URLs - Requires OAuth2 Bearer Token
Full CRUD operations for authenticated users
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DashboardSiteViewSet, DashboardProjectViewSet, DashboardProjectMediaViewSet,
    DashboardExperienceViewSet, DashboardSocialLinkViewSet, DashboardAPIKeyViewSet
)

router = DefaultRouter()
router.register(r'site', DashboardSiteViewSet, basename='dashboard-site')
router.register(r'projects', DashboardProjectViewSet, basename='dashboard-projects')
router.register(r'project-media', DashboardProjectMediaViewSet, basename='dashboard-project-media')
router.register(r'experiences', DashboardExperienceViewSet, basename='dashboard-experiences')
router.register(r'social-links', DashboardSocialLinkViewSet, basename='dashboard-social-links')
router.register(r'api-keys', DashboardAPIKeyViewSet, basename='dashboard-api-keys')

urlpatterns = [
    path('', include(router.urls)),
]
