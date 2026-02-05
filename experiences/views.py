"""
Views for experiences, skills, and social links - Dashboard, Public, and External API access.
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from core.auth.permissions import HasValidAPIKey
from experiences.models import Experience, Skill, SocialLink
from experiences.serializers import ExperienceSerializer, SkillSerializer, SocialLinkSerializer


# ============================================
# Dashboard Views (Authenticated Users)
# ============================================

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


class DashboardSkillViewSet(viewsets.ModelViewSet):
    """
    Dashboard Skill management.
    Full CRUD for user's skills.
    """
    serializer_class = SkillSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Skill.objects.filter(site__user=self.request.user)
    
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


# ============================================
# Public API Views (Domain-based, Read-only)
# ============================================

class PublicExperienceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public API for experiences.
    Read-only access based on site domain.
    """
    serializer_class = ExperienceSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        site = getattr(self.request, 'site', None)
        if not site:
            return Experience.objects.none()
        
        return Experience.objects.filter(site=site, is_published=True)


class PublicSkillViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public API for skills.
    Read-only access based on site domain.
    """
    serializer_class = SkillSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        site = getattr(self.request, 'site', None)
        if not site:
            return Skill.objects.none()
        
        return Skill.objects.filter(site=site, is_published=True)


class PublicSocialLinkViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public API for social links.
    Read-only access based on site domain.
    """
    serializer_class = SocialLinkSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        site = getattr(self.request, 'site', None)
        if not site:
            return SocialLink.objects.none()
        
        return SocialLink.objects.filter(site=site)


# ============================================
# External API Views (API Key Required)
# ============================================

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
        
        return Experience.objects.filter(site=site, is_published=True)


class ExternalSkillViewSet(viewsets.ReadOnlyModelViewSet):
    """
    External API for skills.
    Read-only access with API key.
    """
    serializer_class = SkillSerializer
    permission_classes = [HasValidAPIKey]
    
    def get_queryset(self):
        site = getattr(self.request, 'site', None)
        if not site:
            return Skill.objects.none()
        
        return Skill.objects.filter(site=site, is_published=True)


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
