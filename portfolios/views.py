"""
Views for portfolio sites - Dashboard and Public access.
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from portfolios.models import Site
from portfolios.serializers import SiteDetailSerializer, PublicSiteSerializer, CustomDomainSerializer
from projects.serializers import PublicProjectSerializer
from experiences.serializers import ExperienceSerializer, SocialLinkSerializer, SkillSerializer
from rest_framework import viewsets
from rest_framework.decorators import action
from django.utils import timezone
from portfolios.models import CustomDomain
from core.cloudflare import CloudflareClient

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

class CustomDomainViewSet(viewsets.ModelViewSet):
    """
    CRUD endpoints for Custom Domains.
    User can only access their own site's custom domains.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CustomDomainSerializer

    def get_queryset(self):
        """Only return domains for the authenticated user's site"""
        if hasattr(self.request.user, 'site'):
            return CustomDomain.objects.filter(site=self.request.user.site)
        return CustomDomain.objects.none()

    def perform_create(self, serializer):
        """Auto-associate the domain with the user's site and add to Cloudflare"""
        from billing.gates import check_limit
        from rest_framework.exceptions import PermissionDenied
        
        limit_check = check_limit(self.request.user, "allow_custom_domain", 0)
        if limit_check["upgrade_required"]:
            raise PermissionDenied({
                "error": "upgrade_required",
                "message": "Custom domains are not allowed on your current plan.",
                "upgrade_url": "/pricing"
            })
            
        domain = serializer.validated_data.get('domain')
        cloudflare_id = CloudflareClient.add_custom_hostname(domain)
        serializer.save(site=self.request.user.site, cloudflare_id=cloudflare_id)

    def perform_destroy(self, instance):
        """Delete from Cloudflare when removing domain"""
        if instance.cloudflare_id:
            CloudflareClient.delete_custom_hostname(instance.cloudflare_id)
        instance.delete()

    @extend_schema(
        responses=CustomDomainSerializer,
        description="Verify DNS configuration for the custom domain",
        tags=['Dashboard - Domains']
    )
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify the custom domain status"""
        domain_obj = self.get_object()
        
        if not domain_obj.cloudflare_id:
            # If it has no CF ID, try to create it now
            cf_id = CloudflareClient.add_custom_hostname(domain_obj.domain)
            if cf_id:
                domain_obj.cloudflare_id = cf_id
                domain_obj.save()
            else:
                return Response(
                    {'error': 'Could not register domain with Cloudflare. Please check your settings.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        # Check status from Cloudflare
        cf_data = CloudflareClient.get_custom_hostname(domain_obj.cloudflare_id)
        if not cf_data:
            return Response(
                {'error': 'Could not fetch status from Cloudflare'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        cf_status = cf_data.get('status')
        if cf_status == 'active':
            domain_obj.status = 'verified'
            domain_obj.verified_at = timezone.now()
        elif cf_status in ['pending', 'initializing', 'pending_validation']:
            domain_obj.status = 'pending'
        else:
            domain_obj.status = 'failed'
            
        domain_obj.save()
        return Response(self.get_serializer(domain_obj).data)


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
