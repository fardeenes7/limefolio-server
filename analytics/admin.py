from django.contrib import admin
from analytics.models import SiteVisit


@admin.register(SiteVisit)
class SiteVisitAdmin(admin.ModelAdmin):
    list_display = ["site", "path", "device", "country", "browser", "timestamp"]
    list_filter = ["device", "country", "site"]
    search_fields = ["path", "referrer", "session_id", "site__subdomain"]
    readonly_fields = [
        "site", "path", "referrer", "referrer_domain",
        "country", "device", "browser", "session_id", "timestamp",
    ]
    ordering = ["-timestamp"]

    def has_add_permission(self, request):
        return False  # Visits are only created via the API
