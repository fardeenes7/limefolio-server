from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import BlogPost, BlogComment
from .serializers import (
    BlogPostListSerializer,
    BlogPostDetailSerializer,
    BlogPostCreateUpdateSerializer,
    BlogCommentSerializer
)


class BlogPostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing blog posts
    
    list: Get all blog posts for the authenticated user's site
    retrieve: Get a specific blog post
    create: Create a new blog post
    update: Update a blog post
    partial_update: Partially update a blog post
    destroy: Delete a blog post
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'excerpt', 'content', 'tags', 'categories']
    ordering_fields = ['created_at', 'updated_at', 'published_at', 'view_count', 'title']
    ordering = ['-published_at', '-created_at']
    
    def get_queryset(self):
        """Filter blog posts by the authenticated user's site"""
        user = self.request.user
        queryset = BlogPost.objects.filter(site__user=user)
        
        # Filter by status
        status_param = self.request.query_params.get('status', None)
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        # Filter by featured
        is_featured = self.request.query_params.get('is_featured', None)
        if is_featured is not None:
            queryset = queryset.filter(is_featured=is_featured.lower() == 'true')
        
        # Filter by tags
        tags = self.request.query_params.get('tags', None)
        if tags:
            tag_list = tags.split(',')
            queryset = queryset.filter(tags__overlap=tag_list)
        
        # Filter by categories
        categories = self.request.query_params.get('categories', None)
        if categories:
            category_list = categories.split(',')
            queryset = queryset.filter(categories__overlap=category_list)
        
        return queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return BlogPostListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return BlogPostCreateUpdateSerializer
        return BlogPostDetailSerializer
    
    def perform_create(self, serializer):
        """Set the site when creating a blog post"""
        from billing.gates import check_limit
        from rest_framework.exceptions import PermissionDenied
        
        current_count = BlogPost.objects.filter(site__user=self.request.user).count()
        limit_check = check_limit(self.request.user, "max_blogs", current_count)
        if limit_check["upgrade_required"]:
            raise PermissionDenied({
                "error": "upgrade_required",
                "message": f"You have reached the limit of {limit_check['limit']} blog posts for your current plan.",
                "upgrade_url": "/pricing"
            })
            
        site = self.request.user.site
        
        # Auto-publish if status is published and no published_at date
        if serializer.validated_data.get('status') == 'published' and not serializer.validated_data.get('published_at'):
            serializer.save(site=site, published_at=timezone.now())
        else:
            serializer.save(site=site)
    
    def perform_update(self, serializer):
        """Update published_at when changing status to published"""
        if serializer.validated_data.get('status') == 'published' and not serializer.instance.published_at:
            serializer.save(published_at=timezone.now())
        else:
            serializer.save()
    
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publish a blog post"""
        post = self.get_object()
        post.status = 'published'
        if not post.published_at:
            post.published_at = timezone.now()
        post.save()
        serializer = self.get_serializer(post)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def unpublish(self, request, pk=None):
        """Unpublish a blog post (set to draft)"""
        post = self.get_object()
        post.status = 'draft'
        post.save()
        serializer = self.get_serializer(post)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Archive a blog post"""
        post = self.get_object()
        post.status = 'archived'
        post.save()
        serializer = self.get_serializer(post)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        """Get all comments for a blog post"""
        post = self.get_object()
        comments = post.comments.all()
        
        # Filter by approval status
        is_approved = request.query_params.get('is_approved', None)
        if is_approved is not None:
            comments = comments.filter(is_approved=is_approved.lower() == 'true')
        
        serializer = BlogCommentSerializer(comments, many=True)
        return Response(serializer.data)


class BlogCommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing blog comments
    
    list: Get all comments for the authenticated user's blog posts
    retrieve: Get a specific comment
    create: Create a new comment (public endpoint)
    update: Update a comment (admin only)
    destroy: Delete a comment
    """
    serializer_class = BlogCommentSerializer
    
    def get_permissions(self):
        """Allow anyone to create comments, but require authentication for other actions"""
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        """Filter comments by the authenticated user's blog posts"""
        if self.request.user.is_authenticated:
            return BlogComment.objects.filter(post__site__user=self.request.user)
        return BlogComment.objects.none()
    
    def perform_create(self, serializer):
        """Create a comment on a blog post"""
        post_id = self.request.data.get('post_id')
        post = get_object_or_404(BlogPost, id=post_id, status='published')
        serializer.save(post=post)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a comment"""
        comment = self.get_object()
        comment.is_approved = True
        comment.save()
        serializer = self.get_serializer(comment)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def unapprove(self, request, pk=None):
        """Unapprove a comment"""
        comment = self.get_object()
        comment.is_approved = False
        comment.save()
        serializer = self.get_serializer(comment)
        return Response(serializer.data)
