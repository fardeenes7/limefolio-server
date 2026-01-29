"""
Serializers for portfolio sites and custom domains.
"""
from rest_framework import serializers
from portfolios.models import Site, CustomDomain


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
    custom_domains = CustomDomainSerializer(many=True, read_only=True)
    
    class Meta:
        model = Site
        fields = [
            'id', 'uuid', 'subdomain', 'title', 'tagline', 'description',
            'logo', 'favicon', 'meta_title', 'meta_description',
            'is_published', 'is_active',
            'custom_domains',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'uuid', 'subdomain', 'created_at', 'updated_at']


class PublicSiteSerializer(serializers.ModelSerializer):
    """Public site serializer - minimal info"""
    
    class Meta:
        model = Site
        fields = [
            'title', 'tagline', 'description',
            'logo', 'favicon'
        ]
        read_only_fields = [
            'title', 'tagline', 'description',
            'logo', 'favicon'
        ]
