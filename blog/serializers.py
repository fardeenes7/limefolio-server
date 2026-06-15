from rest_framework import serializers
from .models import BlogPost, BlogComment
from media.serializers import MediaSerializer


class BlogPostListSerializer(serializers.ModelSerializer):
    """Serializer for blog post list view"""
    thumbnail = serializers.SerializerMethodField()
    author_name = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'excerpt', 'thumbnail', 'thumbnail_url',
            'author_name', 'tags', 'categories', 'status',
            'is_featured', 'published_at', 'reading_time',
            'view_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'view_count', 'created_at', 'updated_at']
    
    def get_thumbnail(self, obj):
        return obj.thumbnail
    
    def get_author_name(self, obj):
        return obj.author or obj.site.user.get_full_name() or obj.site.user.username


class BlogPostDetailSerializer(serializers.ModelSerializer):
    """Serializer for blog post detail view"""
    media = MediaSerializer(many=True, read_only=True)
    thumbnail = serializers.SerializerMethodField()
    author_name = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'excerpt', 'content',
            'media', 'thumbnail', 'thumbnail_url', 'author', 'author_name',
            'tags', 'categories', 'meta_description', 'meta_keywords',
            'status', 'is_featured', 'published_at', 'reading_time',
            'view_count', 'comments_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'view_count', 'created_at', 'updated_at']
    
    def get_thumbnail(self, obj):
        return obj.thumbnail
    
    def get_author_name(self, obj):
        return obj.author or obj.site.user.get_full_name() or obj.site.user.username
    
    def get_comments_count(self, obj):
        return obj.comments.filter(is_approved=True).count()


class BlogPostCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating blog posts"""
    
    media_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="List of media IDs to attach to this blog post"
    )

    class Meta:
        model = BlogPost
        fields = [
            'title', 'slug', 'excerpt', 'content', 'thumbnail_url',
            'author', 'tags', 'categories',
            'meta_description', 'meta_keywords',
            'status', 'is_featured', 'published_at', 'media_ids'
        ]
    
    def create(self, validated_data):
        media_ids = validated_data.pop('media_ids', [])
        post = super().create(validated_data)
        
        if media_ids:
            from media.models import Media
            from django.contrib.contenttypes.models import ContentType
            
            content_type = ContentType.objects.get_for_model(BlogPost)
            Media.objects.filter(id__in=media_ids).update(
                content_type=content_type,
                object_id=post.id
            )
        return post
        
    def update(self, instance, validated_data):
        media_ids = validated_data.pop('media_ids', None)
        post = super().update(instance, validated_data)
        
        if media_ids is not None:
            from media.models import Media
            from django.contrib.contenttypes.models import ContentType
            
            content_type = ContentType.objects.get_for_model(BlogPost)
            Media.objects.filter(
                content_type=content_type,
                object_id=post.id
            ).update(content_type=None, object_id=None)
            
            if media_ids:
                Media.objects.filter(id__in=media_ids).update(
                    content_type=content_type,
                    object_id=post.id
                )
        return post
    
    def validate_slug(self, value):
        """Ensure slug is unique for the site"""
        request = self.context.get('request')
        site = request.user.site
        
        # Check if updating existing post
        if self.instance:
            if BlogPost.objects.filter(site=site, slug=value).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("A blog post with this slug already exists.")
        else:
            if BlogPost.objects.filter(site=site, slug=value).exists():
                raise serializers.ValidationError("A blog post with this slug already exists.")
        
        return value


class BlogCommentSerializer(serializers.ModelSerializer):
    """Serializer for blog comments"""
    
    class Meta:
        model = BlogComment
        fields = [
            'id', 'author_name', 'author_email', 'author_website',
            'content', 'is_approved', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_approved', 'created_at', 'updated_at']
    
    def validate_author_email(self, value):
        """Basic email validation"""
        if not value:
            raise serializers.ValidationError("Email is required.")
        return value.lower()
