"""
Serializers for projects and project media.
"""
from rest_framework import serializers
from projects.models import Project, ProjectMedia


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
