"""
Serializers for portfolio sites and custom domains.
"""
from rest_framework import serializers
from portfolios.models import (
    Site,
    CustomDomain,
    PortfolioTemplateConfig,
    TemplateVersionMigrationLog,
    SiteSEO,
)


class CustomDomainSerializer(serializers.ModelSerializer):
    """Serializer for custom domains"""
    
    class Meta:
        model = CustomDomain
        fields = [
            'id', 'domain', 'status', 'verified_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'status', 'verified_at', 'created_at', 'updated_at']

class SiteSEOSerializer(serializers.ModelSerializer):
    """Serializer for SiteSEO"""
    class Meta:
        model = SiteSEO
        fields = [
            'id',
            'default_meta_title', 'default_meta_description',
            'og_image',
            'google_analytics_id', 'google_tag_manager_id', 'facebook_pixel_id',
            'robots_default',
            'page_meta',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SiteListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for site lists"""
    
    class Meta:
        model = Site
        fields = [
            'id', 'uuid', 'subdomain', 'title', 'tagline',
            'is_published', 'available_for_hire', 'created_at'
        ]
        read_only_fields = ['id', 'uuid', 'created_at']


class SiteDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for site with all related data"""
    custom_domains = CustomDomainSerializer(many=True, read_only=True)
    seo = SiteSEOSerializer(read_only=True)
    
    class Meta:
        model = Site
        fields = [
            'id', 'uuid', 'subdomain', 'title', 'tagline', 'description',
            'logo', 'favicon', 'theme', 'template', 'font',
            'is_published', 'is_active', 'available_for_hire',
            'custom_domains', 'seo',
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
    seo = SiteSEOSerializer(read_only=True)
    
    class Meta:
        model = Site
        fields = [
            'title', 'tagline', 'description',
            'theme','template','font', 'logo', 'favicon',
            'available_for_hire', 'seo'
        ]
        read_only_fields = [
            'title', 'tagline', 'description',
            'theme','template','font', 'logo', 'favicon',
            'available_for_hire', 'seo'
        ]


class PortfolioTemplateConfigSerializer(serializers.ModelSerializer):
    """
    Serializer for PortfolioTemplateConfig.

    Exposes raw sparse delta fields only — never the full resolved/merged config.
    The `site` field is excluded from client-writable fields; it is automatically
    set to the requesting user's Site in the view's get_or_create logic.

    Use PATCH (partial=True) for updates — only send the fields that changed.
    Never send a full resolved config here; only the specific delta fields.
    """

    class Meta:
        model = PortfolioTemplateConfig
        fields = [
            'id',
            'template_key',
            'theme_key',
            'font_key',
            'template_version',
            'config_overrides',
            'config_additions',
            'config_removals',
            'config_ordering',
            'theme_overrides',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TemplateVersionMigrationLogSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for TemplateVersionMigrationLog.

    Log entries are created only by management commands (the migration system),
    never via the client API. This serializer is exposed as a read-only list
    endpoint so staff and users can audit migration history.
    """

    class Meta:
        model = TemplateVersionMigrationLog
        fields = [
            'id',
            'template_key',
            'from_version',
            'to_version',
            'changes_applied',
            'migrated_at',
            'migrated_by',
        ]
        read_only_fields = [
            'id',
            'template_key',
            'from_version',
            'to_version',
            'changes_applied',
            'migrated_at',
            'migrated_by',
        ]
