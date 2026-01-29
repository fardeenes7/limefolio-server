"""
Views for portfolio sites - Dashboard and Public access.
"""
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from portfolios.models import Site
from portfolios.serializers import SiteDetailSerializer, PublicSiteSerializer
from projects.serializers import PublicProjectSerializer
from experiences.serializers import ExperienceSerializer, SocialLinkSerializer


# Dashboard Views
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


# Public Views
class PublicSiteDetailView(APIView):
    """
    Get site details with all public content.
    Site is detected from request.site (set by middleware).
    """
    permission_classes = []  # Public access
    
    @extend_schema(
        responses=PublicSiteSerializer,
        description="Get complete site data including projects, experiences, and social links (detected from domain)",
        tags=['Site API']
    )
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
        
        # Get site data
        site_data = PublicSiteSerializer(site).data
        
        # Add projects
        projects = site.projects.filter(is_published=True).order_by('-featured', '-created_at')
        site_data['projects'] = PublicProjectSerializer(projects, many=True).data
        
        # Add experiences
        experiences = site.experiences.filter(is_published=True).order_by('-is_current', '-start_date')
        site_data['experiences'] = ExperienceSerializer(experiences, many=True).data
        
        # Add social links
        social_links = site.social_links.all().order_by('order')
        site_data['social_links'] = SocialLinkSerializer(social_links, many=True).data
        
        return Response(site_data)
