"""
Serializers for the analytics app.
"""

from rest_framework import serializers
from analytics.models import SiteVisit


class TrackVisitSerializer(serializers.Serializer):
    """
    Lightweight write-only serializer for the public tracking endpoint.
    The public portfolio sends this payload on each page load.
    """
    path = serializers.CharField(max_length=500)
    referrer = serializers.CharField(max_length=1000, required=False, allow_blank=True, default="")
    session_id = serializers.CharField(max_length=64)
    device = serializers.ChoiceField(
        choices=["desktop", "mobile", "tablet", "unknown"],
        required=False,
        default="unknown",
    )
    browser = serializers.CharField(max_length=50, required=False, allow_blank=True, default="")


class SiteVisitSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteVisit
        fields = [
            "id", "path", "referrer", "referrer_domain",
            "country", "device", "browser", "session_id", "timestamp",
        ]
        read_only_fields = fields


# ---------------------------------------------------------------------------
# Dashboard stats shapes — these are not model serializers; they exist to
# document the response shape in Swagger.
# ---------------------------------------------------------------------------

class RecentProjectSerializer(serializers.Serializer):
    """Shape of a project card in the dashboard stats response."""
    id = serializers.IntegerField()
    title = serializers.CharField()
    slug = serializers.CharField()
    thumbnail = serializers.CharField(allow_null=True)
    is_published = serializers.BooleanField()
    featured = serializers.BooleanField()
    updated_at = serializers.DateTimeField()
    technologies = serializers.ListField(child=serializers.CharField())


class RecentPostSerializer(serializers.Serializer):
    """Shape of a blog post card in the dashboard stats response."""
    id = serializers.IntegerField()
    title = serializers.CharField()
    slug = serializers.CharField()
    status = serializers.CharField()
    view_count = serializers.IntegerField()
    reading_time = serializers.IntegerField()
    published_at = serializers.DateTimeField(allow_null=True)
    updated_at = serializers.DateTimeField()


class CompletenessItemSerializer(serializers.Serializer):
    key = serializers.CharField()
    label = serializers.CharField()
    done = serializers.BooleanField()
    url = serializers.CharField()


class DashboardStatsSerializer(serializers.Serializer):
    """Full shape of the GET /api/analytics/stats/ response."""
    # Counts
    total_projects = serializers.IntegerField()
    published_projects = serializers.IntegerField()
    total_posts = serializers.IntegerField()
    published_posts = serializers.IntegerField()
    draft_posts = serializers.IntegerField()
    total_skills = serializers.IntegerField()
    total_experiences = serializers.IntegerField()
    total_social_links = serializers.IntegerField()
    total_post_views = serializers.IntegerField()

    # Site health
    is_published = serializers.BooleanField()
    available_for_hire = serializers.BooleanField()
    subdomain = serializers.CharField()
    domain_status = serializers.CharField()  # "none" | "pending" | "verified" | "failed"
    verified_domain = serializers.CharField(allow_null=True)

    # Profile completeness
    completeness_score = serializers.IntegerField()
    completeness_items = CompletenessItemSerializer(many=True)

    # Recent content
    recent_projects = RecentProjectSerializer(many=True)
    recent_posts = RecentPostSerializer(many=True)


class VisitDataPointSerializer(serializers.Serializer):
    date = serializers.DateField()
    visits = serializers.IntegerField()
    unique_visitors = serializers.IntegerField()


class AnalyticsOverviewSerializer(serializers.Serializer):
    """Shape of the GET /api/analytics/overview/ response."""
    days = serializers.IntegerField()
    total_visits = serializers.IntegerField()
    unique_visitors = serializers.IntegerField()
    data = VisitDataPointSerializer(many=True)


class TopPageSerializer(serializers.Serializer):
    path = serializers.CharField()
    visits = serializers.IntegerField()


class TopReferrerSerializer(serializers.Serializer):
    domain = serializers.CharField()
    visits = serializers.IntegerField()


class DeviceBreakdownSerializer(serializers.Serializer):
    device = serializers.CharField()
    visits = serializers.IntegerField()


class CountryBreakdownSerializer(serializers.Serializer):
    country = serializers.CharField()
    visits = serializers.IntegerField()


class AnalyticsBreakdownSerializer(serializers.Serializer):
    """Shape of the GET /api/analytics/breakdown/ response."""
    days = serializers.IntegerField()
    top_pages = TopPageSerializer(many=True)
    top_referrers = TopReferrerSerializer(many=True)
    devices = DeviceBreakdownSerializer(many=True)
    countries = CountryBreakdownSerializer(many=True)
