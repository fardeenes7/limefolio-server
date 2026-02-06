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


class MediaURLSerializer(serializers.ModelSerializer):
    """Serializer for creating media from URLs (presigned URL workflow)"""
    image = serializers.URLField(required=False, allow_null=True, allow_blank=True)
    video = serializers.URLField(required=False, allow_null=True, allow_blank=True)
    thumbnail = serializers.URLField(required=False, allow_null=True, allow_blank=True)
    
    class Meta:
        model = Media
        fields = ['id', 'image', 'video', 'thumbnail', 'alt', 'caption', 'order', 'is_featured', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Ensure at least one media type is provided"""
        if not data.get('image') and not data.get('video'):
            raise serializers.ValidationError("Either image or video must be provided.")
        return data
    
    def create(self, validated_data):
        """Create media instance from URLs"""
        # Extract file keys from URLs
        # URLs come in format: https://domain.com/media/uploads/uuid.ext
        # We need to store: uploads/uuid.ext (storage backend adds 'media/' prefix)
        
        for field in ['image', 'video', 'thumbnail']:
            if validated_data.get(field):
                url = validated_data[field]
                
                # If it's already a path (not a URL), keep it as is
                if not url.startswith('http://') and not url.startswith('https://'):
                    continue
                
                # Extract the file key from the URL
                # Look for '/uploads/' in the URL and extract everything after it
                if '/uploads/' in url:
                    parts = url.split('/uploads/')
                    if len(parts) > 1:
                        file_key = parts[-1]
                        validated_data[field] = f'uploads/{file_key}'
        
        return super().create(validated_data)


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
