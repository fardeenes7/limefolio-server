"""
Dashboard API Views - Requires OAuth2 Bearer Token
Full CRUD operations for authenticated users managing their portfolio
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from portfolio.models import Site, Project, ProjectMedia, Experience, SocialLink, APIKey
from portfolio.serializers import (
    SiteDetailSerializer, ProjectListSerializer, ProjectDetailSerializer,
    ProjectMediaSerializer, ExperienceSerializer, SocialLinkSerializer,
    APIKeySerializer
)


class DashboardSiteViewSet(viewsets.ModelViewSet):
    """
    Dashboard Site management.
    User can only access their own site.
    """
    serializer_class = SiteDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Site.objects.filter(user=self.request.user)
    
    def get_object(self):
        # Always return the user's site
        return self.request.user.site


class DashboardProjectViewSet(viewsets.ModelViewSet):
    """
    Dashboard Project management.
    Full CRUD for user's projects.
    """
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProjectListSerializer
        return ProjectDetailSerializer
    
    def get_queryset(self):
        return Project.objects.filter(site__user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(site=self.request.user.site)


class DashboardProjectMediaViewSet(viewsets.ModelViewSet):
    """
    Dashboard Project Media management.
    """
    serializer_class = ProjectMediaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ProjectMedia.objects.filter(project__site__user=self.request.user)
    
    def perform_create(self, serializer):
        project_id = self.request.data.get('project')
        project = Project.objects.get(id=project_id, site__user=self.request.user)
        serializer.save(project=project)


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


class DashboardAPIKeyViewSet(viewsets.ModelViewSet):
    """
    Dashboard API Key management.
    Users can create and manage API keys for their site.
    """
    serializer_class = APIKeySerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete']  # No PUT
    
    def get_queryset(self):
        return APIKey.objects.filter(site__user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(site=self.request.user.site)
    
    @action(detail=True, methods=['post'])
    def regenerate(self, request, pk=None):
        """Regenerate API key"""
        api_key = self.get_object()
        api_key.key = APIKey.generate_key()
        api_key.save()
        return Response({'key': api_key.key})
    
    @action(detail=True, methods=['post'])
    def reset_secret(self, request, pk=None):
        """Reset API secret"""
        api_key = self.get_object()
        new_secret = APIKey.generate_secret()
        api_key.secret_hash = APIKey.hash_secret(new_secret)
        api_key.save()
        return Response({'secret': new_secret})
