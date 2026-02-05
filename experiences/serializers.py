"""
Serializers for experiences, skills, and social links.
"""
from rest_framework import serializers
from experiences.models import Experience, Skill, SocialLink


class SocialLinkSerializer(serializers.ModelSerializer):
    """Serializer for social media links"""
    
    class Meta:
        model = SocialLink
        fields = ['id', 'platform', 'url', 'username', 'order']
        read_only_fields = ['id']


class SkillSerializer(serializers.ModelSerializer):
    """Serializer for user skills"""
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    proficiency_display = serializers.CharField(source='get_proficiency_display', read_only=True)
    
    class Meta:
        model = Skill
        fields = [
            'id', 'name', 'category', 'category_display', 
            'proficiency', 'proficiency_display',
            'description', 'years_of_experience', 'icon_url',
            'order', 'is_featured', 'is_published'
        ]
        read_only_fields = ['id', 'category_display', 'proficiency_display']


class ExperienceSerializer(serializers.ModelSerializer):
    """Serializer for work experience"""
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = Experience
        fields = [
            'id', 'company', 'position', 'description', 'type', 'type_display',
            'company_logo', 'url', 'location',
            'start_date', 'end_date', 'is_current', 'order',
            'is_published'
        ]
        read_only_fields = ['id', 'type_display']
