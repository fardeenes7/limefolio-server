"""
External API Views - Requires API Key/Secret
Programmatic access for third-party integrations
"""
from rest_framework import viewsets
from rest_framework.response import Response
from portfolio.auth.permissions import HasValidAPIKey
from portfolio.models import Project, Experience, SocialLink
from portfolio.serializers import (
    ProjectListSerializer, ProjectDetailSerializer,
    ExperienceSerializer, SocialLinkSerializer
)


class ExternalProjectViewSet(viewsets.ReadOnlyModelViewSet):
    """
    External API for projects.
    Read-only access with API key.
    """
    permission_classes = [HasValidAPIKey]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProjectListSerializer
        return ProjectDetailSerializer
    
    def get_queryset(self):
        # Get site from API key
        site = getattr(self.request, 'site', None)
        if not site:
            return Project.objects.none()
        
        return Project.objects.filter(site=site)


class ExternalExperienceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    External API for experiences.
    Read-only access with API key.
    """
    serializer_class = ExperienceSerializer
    permission_classes = [HasValidAPIKey]
    
    def get_queryset(self):
        site = getattr(self.request, 'site', None)
        if not site:
            return Experience.objects.none()
        
        return Experience.objects.filter(site=site)


class ExternalSocialLinkViewSet(viewsets.ReadOnlyModelViewSet):
    """
    External API for social links.
    Read-only access with API key.
    """
    serializer_class = SocialLinkSerializer
    permission_classes = [HasValidAPIKey]
    
    def get_queryset(self):
        site = getattr(self.request, 'site', None)
        if not site:
            return SocialLink.objects.none()
        
        return SocialLink.objects.filter(site=site)
