"""
Serializers for projects and project media.
"""
from rest_framework import serializers
from projects.models import Project
from media.serializers import MediaSerializer


class ProjectListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for project lists"""
    media_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'title', 'slug', 'tagline', 'thumbnail',
            'featured', 'is_published', 'media_count', 'created_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at']
    
    def get_media_count(self, obj):
        return obj.media.count()


class ProjectDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for individual projects"""
    media = MediaSerializer(many=True, read_only=True)
    
    class Meta:
        model = Project
        fields = [
            'id', 'title', 'slug', 'tagline', 'description', 'content',
            'thumbnail', 'project_url', 'github_url', 'technologies',
            'featured', 'is_published', 'order', 'media',
            'start_date', 'end_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class PublicProjectSerializer(serializers.ModelSerializer):
    """Public project serializer - only published projects"""
    media = MediaSerializer(many=True, read_only=True)
    
    class Meta:
        model = Project
        fields = [
            'id', 'title', 'slug', 'tagline', 'description', 'content',
            'thumbnail', 'project_url', 'github_url', 'technologies',
            'media', 'start_date', 'end_date', 'created_at'
        ]
        read_only_fields = [
            'id', 'title', 'slug', 'tagline', 'description', 'content',
            'thumbnail', 'project_url', 'github_url', 'technologies',
            'media', 'start_date', 'end_date', 'created_at'
        ]
