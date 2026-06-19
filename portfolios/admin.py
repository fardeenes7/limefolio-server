from django.contrib import admin
from portfolios.models import (
    Site,
    CustomDomain,
    PortfolioTemplateConfig,
    TemplateVersionMigrationLog,
)


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ['title', 'subdomain', 'user', 'is_published', 'is_active', 'created_at']
    list_filter = ['is_published', 'is_active', 'available_for_hire']
    search_fields = ['title', 'subdomain', 'user__username', 'user__email']
    readonly_fields = ['uuid', 'created_at', 'updated_at']


@admin.register(CustomDomain)
class CustomDomainAdmin(admin.ModelAdmin):
    list_display = ['domain', 'site', 'status', 'verified_at', 'created_at']
    list_filter = ['status']
    search_fields = ['domain', 'site__title', 'site__subdomain']
    readonly_fields = ['verification_token', 'verified_at', 'cloudflare_id', 'created_at', 'updated_at']


@admin.register(PortfolioTemplateConfig)
class PortfolioTemplateConfigAdmin(admin.ModelAdmin):
    """
    Admin for PortfolioTemplateConfig.
    Displays key config metadata; JSON delta fields are shown but should not be
    edited manually — use management commands for bulk migrations.
    """
    list_display = ['site', 'template_key', 'theme_key', 'font_key', 'template_version', 'updated_at']
    list_filter = ['template_key', 'template_version']
    search_fields = ['site__title', 'site__subdomain', 'site__user__email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(TemplateVersionMigrationLog)
class TemplateVersionMigrationLogAdmin(admin.ModelAdmin):
    """
    Admin for TemplateVersionMigrationLog.
    Read-only — log entries are written by management commands only.
    """
    list_display = ['config', 'template_key', 'from_version', 'to_version', 'migrated_by', 'migrated_at']
    list_filter = ['template_key', 'from_version', 'to_version', 'migrated_by']
    search_fields = ['config__site__title', 'config__site__subdomain']
    readonly_fields = [
        'config', 'template_key', 'from_version', 'to_version',
        'changes_applied', 'migrated_at', 'migrated_by',
    ]

    def has_add_permission(self, request):
        """Log entries are written by management commands only — block manual creation."""
        return False

    def has_change_permission(self, request, obj=None):
        """Log entries are immutable audit records — block editing."""
        return False
