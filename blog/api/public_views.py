"""
Public API views for blog posts.
Domain-based access for published blog posts.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from blog.models import BlogPost
from blog.serializers import BlogPostDetailSerializer, BlogCommentSerializer


class PublicBlogPostListView(APIView):
    """
    List all published blog posts for the site.
    Public access via domain detection.
    """
    permission_classes = []  # Public access
    
    @extend_schema(
        responses=BlogPostDetailSerializer(many=True),
        description="Get all published blog posts for the current site (detected from domain)",
        tags=['Site API'],
        parameters=[
            OpenApiParameter(
                name='tag',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by tag',
                required=False
            ),
            OpenApiParameter(
                name='category',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by category',
                required=False
            ),
            OpenApiParameter(
                name='featured',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Filter by featured posts',
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
        
        # Get published posts
        posts = BlogPost.objects.filter(
            site=site,
            status='published'
        ).order_by('-published_at')
        
        # Apply filters
        tag = request.query_params.get('tag')
        if tag:
            posts = posts.filter(tags__contains=[tag])
        
        category = request.query_params.get('category')
        if category:
            posts = posts.filter(categories__contains=[category])
        
        featured = request.query_params.get('featured')
        if featured is not None:
            is_featured = featured.lower() == 'true'
            posts = posts.filter(is_featured=is_featured)
        
        serializer = BlogPostDetailSerializer(posts, many=True)
        return Response(serializer.data)


class PublicBlogPostDetailView(APIView):
    """
    Get single published blog post by slug.
    Public access via domain detection.
    """
    permission_classes = []  # Public access
    
    @extend_schema(
        responses=BlogPostDetailSerializer,
        parameters=[
            OpenApiParameter(
                name='slug',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description='Blog post slug'
            )
        ],
        description="Get a single published blog post by slug",
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
            post = BlogPost.objects.get(
                site=site,
                slug=slug,
                status='published'
            )
            
            # Increment view count
            post.view_count += 1
            post.save(update_fields=['view_count'])
            
        except BlogPost.DoesNotExist:
            return Response(
                {'error': 'Blog post not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = BlogPostDetailSerializer(post)
        return Response(serializer.data)


class PublicBlogPostCommentsView(APIView):
    """
    Get approved comments for a blog post.
    Public access via domain detection.
    """
    permission_classes = []  # Public access
    
    @extend_schema(
        responses=BlogCommentSerializer(many=True),
        parameters=[
            OpenApiParameter(
                name='slug',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description='Blog post slug'
            )
        ],
        description="Get all approved comments for a blog post",
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
            post = BlogPost.objects.get(
                site=site,
                slug=slug,
                status='published'
            )
        except BlogPost.DoesNotExist:
            return Response(
                {'error': 'Blog post not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get approved comments only
        comments = post.comments.filter(is_approved=True).order_by('-created_at')
        serializer = BlogCommentSerializer(comments, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        request=BlogCommentSerializer,
        responses=BlogCommentSerializer,
        description="Create a new comment on a blog post (requires moderation)",
        tags=['Site API']
    )
    def post(self, request, slug):
        site = getattr(request, 'site', None)
        
        if not site:
            return Response(
                {'error': 'Site not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            post = BlogPost.objects.get(
                site=site,
                slug=slug,
                status='published'
            )
        except BlogPost.DoesNotExist:
            return Response(
                {'error': 'Blog post not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = BlogCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(post=post)
            return Response(
                {
                    'message': 'Comment submitted successfully. It will appear after moderation.',
                    'comment': serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PublicBlogTagsView(APIView):
    """
    Get all tags used in published blog posts for the site.
    """
    permission_classes = []  # Public access
    
    @extend_schema(
        responses={'type': 'array', 'items': {'type': 'string'}},
        description="Get all unique tags from published blog posts",
        tags=['Site API']
    )
    def get(self, request):
        site = getattr(request, 'site', None)
        
        if not site:
            return Response(
                {'error': 'Site not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get all published posts
        posts = BlogPost.objects.filter(site=site, status='published')
        
        # Collect all unique tags
        tags = set()
        for post in posts:
            if post.tags:
                tags.update(post.tags)
        
        return Response(sorted(list(tags)))


class PublicBlogCategoriesView(APIView):
    """
    Get all categories used in published blog posts for the site.
    """
    permission_classes = []  # Public access
    
    @extend_schema(
        responses={'type': 'array', 'items': {'type': 'string'}},
        description="Get all unique categories from published blog posts",
        tags=['Site API']
    )
    def get(self, request):
        site = getattr(request, 'site', None)
        
        if not site:
            return Response(
                {'error': 'Site not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get all published posts
        posts = BlogPost.objects.filter(site=site, status='published')
        
        # Collect all unique categories
        categories = set()
        for post in posts:
            if post.categories:
                categories.update(post.categories)
        
        return Response(sorted(list(categories)))
