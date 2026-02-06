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
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at']
    
    def validate_subdomain(self, value):
        """Validate that subdomain is not reserved"""
        from portfolios.models import RESERVED_SUBDOMAINS
        
        if value and value.lower() in RESERVED_SUBDOMAINS:
            raise serializers.ValidationError(
                f"Subdomain '{value}' is reserved and cannot be used."
            )
        
        # Check for uniqueness (excluding current instance if updating)
        queryset = Site.objects.filter(subdomain=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError(
                f"Subdomain '{value}' is already taken."
            )
        
        return value


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
