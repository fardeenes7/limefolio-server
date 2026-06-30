"""
Public API views for media.
Domain-based access for site media.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.contrib.contenttypes.models import ContentType

from media.models import Media
from media.serializers import MediaSerializer


class PublicMediaListView(APIView):
    """
    List all media for the site.
    Public access via domain detection.
    """
    permission_classes = []  # Public access
    
    @extend_schema(
        responses=MediaSerializer(many=True),
        description="Get all media for the current site (detected from domain)",
        tags=['Site API'],
        parameters=[
            OpenApiParameter(
                name='content_type',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by content type (e.g., project, blogpost)',
                required=False
            ),
            OpenApiParameter(
                name='media_type',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by media type (image or video)',
                required=False
            ),
            OpenApiParameter(
                name='featured',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Filter by featured media',
                required=False
            ),
        ]
    )
    def get(self, request):
        site = getattr(request, 'site', None)
        
        if not site:
            return Response(
                {'error': 'Site not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get all media related to site content
        # We need to filter by content that belongs to the site
        from projects.models import Project
        from blog.models import BlogPost
        
        # Get content type IDs
        project_ct = ContentType.objects.get_for_model(Project)
        blogpost_ct = ContentType.objects.get_for_model(BlogPost)
        
        is_owner = request.user and request.user.is_authenticated and hasattr(request.user, 'site') and request.user.site == site

        # Get IDs of site's projects and blog posts
        if is_owner:
            project_ids = list(site.projects.values_list('id', flat=True))
            blogpost_ids = list(site.blog_posts.values_list('id', flat=True))
        else:
            project_ids = list(site.projects.filter(is_published=True).values_list('id', flat=True))
            blogpost_ids = list(site.blog_posts.filter(status='published').values_list('id', flat=True))
        
        # Build query
        media = Media.objects.none()
        
        # Add project media
        if project_ids:
            project_media = Media.objects.filter(
                content_type=project_ct,
                object_id__in=project_ids
            )
            media = media | project_media
        
        # Add blog post media
        if blogpost_ids:
            blogpost_media = Media.objects.filter(
                content_type=blogpost_ct,
                object_id__in=blogpost_ids
            )
            media = media | blogpost_media
        
        # Apply filters
        content_type_param = request.query_params.get('content_type')
        if content_type_param:
            if content_type_param.lower() == 'project':
                media = media.filter(content_type=project_ct)
            elif content_type_param.lower() == 'blogpost':
                media = media.filter(content_type=blogpost_ct)
        
        media_type_param = request.query_params.get('media_type')
        if media_type_param:
            if media_type_param.lower() == 'image':
                media = media.filter(image__isnull=False)
            elif media_type_param.lower() == 'video':
                media = media.filter(video__isnull=False)
        
        featured = request.query_params.get('featured')
        if featured is not None:
            is_featured = featured.lower() == 'true'
            media = media.filter(is_featured=is_featured)
        
        # Order by featured and order
        media = media.order_by('-is_featured', 'order', '-created_at')
        
        serializer = MediaSerializer(media, many=True)
        return Response(serializer.data)


class PublicMediaDetailView(APIView):
    """
    Get single media item by ID.
    Public access via domain detection.
    """
    permission_classes = []  # Public access
    
    @extend_schema(
        responses=MediaSerializer,
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Media ID'
            )
        ],
        description="Get a single media item by ID",
        tags=['Site API']
    )
    def get(self, request, id):
        site = getattr(request, 'site', None)
        
        if not site:
            return Response(
                {'error': 'Site not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            media = Media.objects.get(id=id)
            
            # Verify media belongs to site content
            from projects.models import Project
            from blog.models import BlogPost
            
            content_object = media.content_object
            
            # Check if it's a project or blog post belonging to this site
            is_valid = False
            if isinstance(content_object, Project):
                is_valid = content_object.site == site and content_object.is_published
            elif isinstance(content_object, BlogPost):
                is_valid = content_object.site == site and content_object.status == 'published'
            
            if not is_valid:
                return Response(
                    {'error': 'Media not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
        except Media.DoesNotExist:
            return Response(
                {'error': 'Media not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = MediaSerializer(media)
        return Response(serializer.data)
