"""
Serializers for API keys.
"""
from rest_framework import serializers
from core.models import APIKey


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
