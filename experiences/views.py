"""
Views for experiences and social links - Dashboard and External API access.
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from core.auth.permissions import HasValidAPIKey
from experiences.models import Experience, SocialLink
from experiences.serializers import ExperienceSerializer, SocialLinkSerializer


# Dashboard Views
class DashboardExperienceViewSet(viewsets.ModelViewSet):
    """
    Dashboard Experience management.
    Full CRUD for user's work experience.
    """
    serializer_class = ExperienceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Experience.objects.filter(site__user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(site=self.request.user.site)


class DashboardSocialLinkViewSet(viewsets.ModelViewSet):
    """
    Dashboard Social Link management.
    """
    serializer_class = SocialLinkSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return SocialLink.objects.filter(site__user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(site=self.request.user.site)


# External API Views
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
