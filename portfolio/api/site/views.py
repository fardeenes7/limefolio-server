"""
Site API Views - Domain-based, Public Read-Only
Serves portfolio data based on subdomain or custom domain
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from portfolio.serializers.public import PublicSiteSerializer, PublicProjectSerializer
from portfolio.models import Project


class SiteDetailView(APIView):
    """
    Get site details with all public content.
    Site is detected from request.site (set by middleware).
    """
    permission_classes = []  # Public access
    
    def get(self, request):
        site = getattr(request, 'site', None)
        
        if not site:
            return Response(
                {'error': 'Site not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not site.is_published:
            return Response(
                {'error': 'Site is not published'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = PublicSiteSerializer(site)
        return Response(serializer.data)


class SiteProjectListView(APIView):
    """
    List all published projects for the site.
    """
    permission_classes = []  # Public access
    
    def get(self, request):
        site = getattr(request, 'site', None)
        
        if not site:
            return Response(
                {'error': 'Site not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        projects = site.projects.filter(status='published').order_by('-featured', '-created_at')
        serializer = PublicProjectSerializer(projects, many=True)
        return Response(serializer.data)


class SiteProjectDetailView(APIView):
    """
    Get single project by slug.
    """
    permission_classes = []  # Public access
    
    def get(self, request, slug):
        site = getattr(request, 'site', None)
        
        if not site:
            return Response(
                {'error': 'Site not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            project = site.projects.get(slug=slug, status='published')
        except Project.DoesNotExist:
            return Response(
                {'error': 'Project not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = PublicProjectSerializer(project)
        return Response(serializer.data)
