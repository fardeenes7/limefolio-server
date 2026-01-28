"""
Serializers for experiences and social links.
"""
from rest_framework import serializers
from experiences.models import Experience, SocialLink


class SocialLinkSerializer(serializers.ModelSerializer):
    """Serializer for social media links"""
    
    class Meta:
        model = SocialLink
        fields = ['id', 'platform', 'url', 'username', 'order']
        read_only_fields = ['id']


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
