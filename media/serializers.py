from rest_framework import serializers
from .models import Media


class MediaSerializer(serializers.ModelSerializer):
    """Serializer for Media model"""
    media_type = serializers.ReadOnlyField()
    url = serializers.ReadOnlyField()
    
    class Meta:
        model = Media
        fields = [
            'id', 'image', 'video', 'thumbnail',
            'alt', 'caption', 'order', 'is_featured',
            'media_type', 'url', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Ensure at least one media type is provided"""
        if not data.get('image') and not data.get('video'):
            raise serializers.ValidationError("Either image or video must be provided.")
        return data


class MediaCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating media"""
    
    class Meta:
        model = Media
        fields = ['image', 'video', 'thumbnail', 'alt', 'caption', 'order', 'is_featured']
    
    def validate(self, data):
        """Ensure at least one media type is provided"""
        if not data.get('image') and not data.get('video'):
            raise serializers.ValidationError("Either image or video must be provided.")
        return data
