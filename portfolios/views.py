"""
Views for portfolio sites - Dashboard and Public access.
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from portfolios.models import Site
from portfolios.serializers import SiteDetailSerializer, PublicSiteSerializer
from projects.serializers import PublicProjectSerializer
from experiences.serializers import ExperienceSerializer, SocialLinkSerializer, SkillSerializer


# Dashboard Views
class DashboardSiteView(APIView):
    """
    Dashboard Site management.
    User can only access their own site.
    GET: Retrieve the user's site
    PATCH: Update the user's site
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SiteDetailSerializer
    
    @extend_schema(
        responses=SiteDetailSerializer,
        description="Get the authenticated user's site details",
        tags=['Dashboard - Site']
    )
    def get(self, request):
        """Get the user's site"""
        try:
            site = request.user.site
            serializer = SiteDetailSerializer(site)
            return Response(serializer.data)
        except Site.DoesNotExist:
            return Response(
                {'error': 'Site not found. Please create a site first.'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @extend_schema(
        request=SiteDetailSerializer,
        responses=SiteDetailSerializer,
        description="Update the authenticated user's site",
        tags=['Dashboard - Site']
    )
    def patch(self, request):
        """Update the user's site"""
        try:
            site = request.user.site
            serializer = SiteDetailSerializer(site, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Site.DoesNotExist:
            return Response(
                {'error': 'Site not found. Please create a site first.'},
                status=status.HTTP_404_NOT_FOUND
            )


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
        
        # Add skills
        skills = site.skills.filter(is_published=True).order_by('-is_featured', 'category', 'order')
        site_data['skills'] = SkillSerializer(skills, many=True).data

        # Add social links
        social_links = site.social_links.all().order_by('order')
        site_data['social_links'] = SocialLinkSerializer(social_links, many=True).data
        
        return Response(site_data)
