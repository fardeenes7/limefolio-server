"""
Public serializers for site API (domain-based, read-only).
Excludes sensitive information and unpublished content.
"""
from rest_framework import serializers
from portfolio.serializers import (
    SocialLinkSerializer, ProjectMediaSerializer,
    ExperienceSerializer
)
from portfolio.models import Site, Project


class PublicProjectSerializer(serializers.ModelSerializer):
    """Public project serializer - only published projects"""
    media = ProjectMediaSerializer(many=True, read_only=True)
    
    class Meta:
        model = Project
        fields = [
            'id', 'title', 'slug', 'tagline', 'description',
            'thumbnail', 'demo_url', 'github_url', 'technologies',
            'media', 'created_at'
        ]
        read_only_fields = '__all__'


class PublicSiteSerializer(serializers.ModelSerializer):
    """Public site serializer with all public content"""
    social_links = SocialLinkSerializer(many=True, read_only=True)
    projects = serializers.SerializerMethodField()
    experiences = serializers.SerializerMethodField()
    
    class Meta:
        model = Site
        fields = [
            'title', 'tagline', 'description',
            'logo', 'favicon',
            'social_links', 'projects', 'experiences'
        ]
        read_only_fields = '__all__'
    
    def get_projects(self, obj):
        projects = obj.projects.filter(status='published').order_by('-featured', '-created_at')
        return PublicProjectSerializer(projects, many=True).data
    
    def get_experiences(self, obj):
        experiences = obj.experiences.filter(is_published=True).order_by('-is_current', '-start_date')
        return ExperienceSerializer(experiences, many=True).data
