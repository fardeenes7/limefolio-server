"""
Views for projects - Dashboard, Public, and External API access.
"""
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from core.auth.permissions import HasValidAPIKey
from projects.models import Project, ProjectMedia
from projects.serializers import (
    ProjectListSerializer, ProjectDetailSerializer,
    ProjectMediaSerializer, PublicProjectSerializer
)


# Dashboard Views
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


# Public Views
class PublicProjectListView(APIView):
    """
    List all published projects for the site.
    """
    permission_classes = []  # Public access
    
    @extend_schema(
        responses=PublicProjectSerializer(many=True),
        description="Get all published projects for the current site (detected from domain)",
        tags=['Site API']
    )
    def get(self, request):
        site = getattr(request, 'site', None)
        
        if not site:
            return Response(
                {'error': 'Site not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        projects = site.projects.filter(is_published=True).order_by('-featured', '-created_at')
        serializer = PublicProjectSerializer(projects, many=True)
        return Response(serializer.data)


class PublicProjectDetailView(APIView):
    """
    Get single project by slug.
    """
    permission_classes = []  # Public access
    
    @extend_schema(
        responses=PublicProjectSerializer,
        parameters=[
            OpenApiParameter(
                name='slug',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description='Project slug'
            )
        ],
        description="Get a single published project by slug",
        tags=['Site API']
    )
    def get(self, request, slug):
        site = getattr(request, 'site', None)
        
        if not site:
            return Response(
                {'error': 'Site not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            project = site.projects.get(slug=slug, is_published=True)
        except Project.DoesNotExist:
            return Response(
                {'error': 'Project not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = PublicProjectSerializer(project)
        return Response(serializer.data)


# External API Views
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
