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
    media_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="List of media IDs to attach to this project"
    )
    
    class Meta:
        model = Project
        fields = [
            'id', 'title', 'slug', 'tagline', 'description', 'content',
            'thumbnail', 'project_url', 'github_url', 'technologies',
            'featured', 'is_published', 'order', 'media', 'media_ids',
            'start_date', 'end_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        media_ids = validated_data.pop('media_ids', [])
        project = super().create(validated_data)
        
        # Attach media to project
        if media_ids:
            from media.models import Media
            from django.contrib.contenttypes.models import ContentType
            
            content_type = ContentType.objects.get_for_model(Project)
            Media.objects.filter(id__in=media_ids).update(
                content_type=content_type,
                object_id=project.id
            )
        
        return project
    
    def update(self, instance, validated_data):
        media_ids = validated_data.pop('media_ids', None)
        project = super().update(instance, validated_data)
        
        # Update media attachments if provided
        if media_ids is not None:
            from media.models import Media
            from django.contrib.contenttypes.models import ContentType
            
            content_type = ContentType.objects.get_for_model(Project)
            
            # Clear existing media attachments
            Media.objects.filter(
                content_type=content_type,
                object_id=project.id
            ).update(content_type=None, object_id=None)
            
            # Attach new media
            if media_ids:
                Media.objects.filter(id__in=media_ids).update(
                    content_type=content_type,
                    object_id=project.id
                )
        
        return project


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
