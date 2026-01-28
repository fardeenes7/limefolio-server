"""
Base serializers for portfolio models.
Used across different API types with different permission levels.
"""
from rest_framework import serializers
from portfolio.models import (
    Site, CustomDomain, Project, ProjectMedia,
    Experience, SocialLink, APIKey
)


class SocialLinkSerializer(serializers.ModelSerializer):
    """Serializer for social media links"""
    
    class Meta:
        model = SocialLink
        fields = ['id', 'platform', 'url', 'username', 'order']
        read_only_fields = ['id']


class ProjectMediaSerializer(serializers.ModelSerializer):
    """Serializer for project media"""
    
    class Meta:
        model = ProjectMedia
        fields = ['id', 'image', 'thumbnail', 'caption', 'order', 'media_type']
        read_only_fields = ['id']


class ProjectListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for project lists"""
    media_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'title', 'slug', 'tagline', 'thumbnail',
            'featured', 'status', 'media_count', 'created_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at']
    
    def get_media_count(self, obj):
        return obj.media.count()


class ProjectDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for individual projects"""
    media = ProjectMediaSerializer(many=True, read_only=True)
    
    class Meta:
        model = Project
        fields = [
            'id', 'title', 'slug', 'tagline', 'description',
            'thumbnail', 'demo_url', 'github_url', 'technologies',
            'featured', 'status', 'order', 'media',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class ExperienceSerializer(serializers.ModelSerializer):
    """Serializer for work experience"""
    
    class Meta:
        model = Experience
        fields = [
            'id', 'company', 'position', 'description', 'type',
            'company_logo', 'url', 'location',
            'start_date', 'end_date', 'is_current', 'order',
            'is_published'
        ]
        read_only_fields = ['id']


class CustomDomainSerializer(serializers.ModelSerializer):
    """Serializer for custom domains"""
    
    class Meta:
        model = CustomDomain
        fields = [
            'id', 'domain', 'status', 'verified_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'status', 'verified_at', 'created_at', 'updated_at']


class SiteListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for site lists"""
    
    class Meta:
        model = Site
        fields = [
            'id', 'uuid', 'subdomain', 'title', 'tagline',
            'is_published', 'created_at'
        ]
        read_only_fields = ['id', 'uuid', 'created_at']


class SiteDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for site with all related data"""
    social_links = SocialLinkSerializer(many=True, read_only=True)
    custom_domains = CustomDomainSerializer(many=True, read_only=True)
    projects_count = serializers.SerializerMethodField()
    experiences_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Site
        fields = [
            'id', 'uuid', 'subdomain', 'title', 'tagline', 'description',
            'logo', 'favicon', 'meta_title', 'meta_description',
            'is_published', 'is_active',
            'social_links', 'custom_domains',
            'projects_count', 'experiences_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'uuid', 'subdomain', 'created_at', 'updated_at']
    
    def get_projects_count(self, obj):
        return obj.projects.filter(status='published').count()
    
    def get_experiences_count(self, obj):
        return obj.experiences.filter(is_published=True).count()


class APIKeySerializer(serializers.ModelSerializer):
    """Serializer for API keys (never expose secret_hash)"""
    secret = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = APIKey
        fields = [
            'id', 'name', 'key', 'secret', 'is_active', 'read_only',
            'rate_limit', 'request_count', 'last_used_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'key', 'request_count', 'last_used_at',
            'created_at', 'updated_at'
        ]
    
    def create(self, validated_data):
        secret = validated_data.pop('secret', None)
        if not secret:
            secret = APIKey.generate_secret()
        
        api_key = APIKey(**validated_data)
        api_key.secret_hash = APIKey.hash_secret(secret)
        api_key.save()
        
        # Attach secret to instance for response (won't be saved)
        api_key.secret = secret
        return api_key
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Only include secret on creation
        if not hasattr(instance, 'secret'):
            data.pop('secret', None)
        return data
