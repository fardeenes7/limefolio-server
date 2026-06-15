"""
Views for the analytics app.

Endpoints:
  POST /api/analytics/track/        — public, record a page visit
  GET  /api/analytics/stats/        — auth, dashboard KPI aggregation
  GET  /api/analytics/overview/     — auth, daily visit time-series
  GET  /api/analytics/breakdown/    — auth, top pages / referrers / devices / countries
"""

import re
from urllib.parse import urlparse
from datetime import timedelta, date

from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncDate
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from analytics.models import SiteVisit
from analytics.serializers import (
    TrackVisitSerializer,
    DashboardStatsSerializer,
    AnalyticsOverviewSerializer,
    AnalyticsBreakdownSerializer,
)
from blog.models import BlogPost
from experiences.models import Experience, Skill, SocialLink
from portfolios.models import CustomDomain, Site
from projects.models import Project


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_referrer_domain(referrer: str) -> str:
    """Extract the bare domain from a referrer URL."""
    if not referrer:
        return ""
    try:
        parsed = urlparse(referrer)
        domain = parsed.netloc or ""
        # strip www.
        domain = re.sub(r"^www\.", "", domain)
        return domain.lower()
    except Exception:
        return ""


def _parse_days(request, default: int = 30) -> int:
    """Parse ?days= query param, clamped to 1–365."""
    try:
        days = int(request.query_params.get("days", default))
        return max(1, min(days, 365))
    except (ValueError, TypeError):
        return default


def _completeness(site) -> tuple[int, list[dict]]:
    """
    Calculate portfolio completeness score (0-100) and checklist items.
    Returns (score, items_list).
    """
    checks = [
        {
            "key": "published",
            "label": "Site is published",
            "done": site.is_published,
            "url": "/app/site",
        },
        {
            "key": "logo",
            "label": "Logo / profile image uploaded",
            "done": bool(site.logo),
            "url": "/app/site",
        },
        {
            "key": "tagline",
            "label": "Tagline or bio added",
            "done": bool(site.tagline and site.tagline.strip()),
            "url": "/app/site",
        },
        {
            "key": "projects",
            "label": "At least 1 project added",
            "done": site.projects.filter(is_published=True).exists(),
            "url": "/app/projects",
        },
        {
            "key": "experience",
            "label": "At least 1 experience added",
            "done": site.experiences.filter(is_published=True).exists(),
            "url": "/app/experiences",
        },
        {
            "key": "skills",
            "label": "At least 3 skills added",
            "done": site.skills.filter(is_published=True).count() >= 3,
            "url": "/app/skills",
        },
        {
            "key": "blog",
            "label": "At least 1 blog post published",
            "done": site.blog_posts.filter(status="published").exists(),
            "url": "/app/posts",
        },
        {
            "key": "social_links",
            "label": "Social links added",
            "done": site.social_links.exists(),
            "url": "/app/social-links",
        },
        {
            "key": "custom_domain",
            "label": "Custom domain connected",
            "done": site.custom_domains.filter(status="verified").exists(),
            "url": "/app/site/domains",
        },
        {
            "key": "hire",
            "label": '"Available for hire" status set',
            "done": site.available_for_hire,
            "url": "/app/site",
        },
    ]

    done_count = sum(1 for c in checks if c["done"])
    score = round((done_count / len(checks)) * 100)
    return score, checks


# ---------------------------------------------------------------------------
# View: TrackVisitView  (public — no auth required)
# ---------------------------------------------------------------------------

class TrackVisitView(APIView):
    """
    Record a page visit on a portfolio site.

    Called by the public portfolio frontend on each page load.
    The site is identified by the X-Site-ID header (UUID of the site)
    or falls back to the site detected by the SiteDetectionMiddleware.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        request=TrackVisitSerializer,
        responses={201: None},
        description=(
            "Record a page view for a portfolio site. "
            "Send the site UUID in the X-Site-ID header. "
            "No authentication required."
        ),
        tags=["Analytics - Tracking"],
    )
    def post(self, request):
        serializer = TrackVisitSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        # Resolve site: prefer X-Site-ID header (UUID), fall back to middleware
        site = getattr(request, "site", None)
        site_uuid = request.headers.get("X-Site-ID")
        if site_uuid and not site:
            try:
                site = Site.objects.get(uuid=site_uuid)
            except Site.DoesNotExist:
                pass

        if not site:
            return Response(
                {"error": "Could not identify the portfolio site."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        referrer = data.get("referrer", "")
        SiteVisit.objects.create(
            site=site,
            path=data["path"],
            referrer=referrer,
            referrer_domain=_extract_referrer_domain(referrer),
            device=data.get("device", "unknown"),
            browser=data.get("browser", ""),
            session_id=data["session_id"],
        )

        return Response(status=status.HTTP_201_CREATED)


# ---------------------------------------------------------------------------
# View: DashboardStatsView  (authenticated)
# ---------------------------------------------------------------------------

class DashboardStatsView(APIView):
    """
    Return all KPIs and recent content for the dashboard home page.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses=DashboardStatsSerializer,
        description="Aggregate dashboard stats for the authenticated user's site.",
        tags=["Analytics - Dashboard"],
    )
    def get(self, request):
        try:
            site = request.user.site
        except Site.DoesNotExist:
            return Response(
                {"error": "Site not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # --- Content counts ---
        projects = Project.objects.filter(site=site)
        posts = BlogPost.objects.filter(site=site)
        skills = Skill.objects.filter(site=site)
        experiences = Experience.objects.filter(site=site)
        social_links = SocialLink.objects.filter(site=site)

        total_post_views = posts.aggregate(total=Sum("view_count"))["total"] or 0

        # --- Site health ---
        verified_domain = site.custom_domains.filter(status="verified").first()
        pending_domain = site.custom_domains.filter(status="pending").first()
        failed_domain = site.custom_domains.filter(status="failed").first()

        if verified_domain:
            domain_status = "verified"
        elif pending_domain:
            domain_status = "pending"
        elif failed_domain:
            domain_status = "failed"
        else:
            domain_status = "none"

        # --- Profile completeness ---
        score, completeness_items = _completeness(site)

        # --- Recent projects (last 4) ---
        recent_projects = []
        for p in projects.order_by("-updated_at")[:4]:
            recent_projects.append(
                {
                    "id": p.id,
                    "title": p.title,
                    "slug": p.slug,
                    "thumbnail": p.thumbnail,
                    "is_published": p.is_published,
                    "featured": p.featured,
                    "updated_at": p.updated_at,
                    "technologies": p.technologies or [],
                }
            )

        # --- Recent posts (last 4) ---
        recent_posts = []
        for post in posts.order_by("-updated_at")[:4]:
            recent_posts.append(
                {
                    "id": post.id,
                    "title": post.title,
                    "slug": post.slug,
                    "status": post.status,
                    "view_count": post.view_count,
                    "reading_time": post.reading_time,
                    "published_at": post.published_at,
                    "updated_at": post.updated_at,
                }
            )

        return Response(
            {
                # Counts
                "total_projects": projects.count(),
                "published_projects": projects.filter(is_published=True).count(),
                "total_posts": posts.count(),
                "published_posts": posts.filter(status="published").count(),
                "draft_posts": posts.filter(status="draft").count(),
                "total_skills": skills.count(),
                "total_experiences": experiences.count(),
                "total_social_links": social_links.count(),
                "total_post_views": total_post_views,
                # Site health
                "is_published": site.is_published,
                "available_for_hire": site.available_for_hire,
                "subdomain": site.subdomain,
                "domain_status": domain_status,
                "verified_domain": verified_domain.domain if verified_domain else None,
                # Completeness
                "completeness_score": score,
                "completeness_items": completeness_items,
                # Recent content
                "recent_projects": recent_projects,
                "recent_posts": recent_posts,
            }
        )


# ---------------------------------------------------------------------------
# View: AnalyticsOverviewView  (authenticated)
# ---------------------------------------------------------------------------

class AnalyticsOverviewView(APIView):
    """
    Return daily visit time-series for the analytics page chart.
    Query params:
      days (int, default=30): number of days to look back (1–365)
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "days",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Number of days to include (default 30, max 365)",
            )
        ],
        responses=AnalyticsOverviewSerializer,
        description="Daily visit time-series for the authenticated user's site.",
        tags=["Analytics - Dashboard"],
    )
    def get(self, request):
        try:
            site = request.user.site
        except Site.DoesNotExist:
            return Response({"error": "Site not found."}, status=status.HTTP_404_NOT_FOUND)

        days = _parse_days(request)
        since = timezone.now() - timedelta(days=days)

        visits_qs = SiteVisit.objects.filter(site=site, timestamp__gte=since)

        # Aggregate by day
        by_day = (
            visits_qs.annotate(date=TruncDate("timestamp"))
            .values("date")
            .annotate(
                visits=Count("id"),
                unique_visitors=Count("session_id", distinct=True),
            )
            .order_by("date")
        )

        # Build a complete date range (fill gaps with zeros)
        data_map: dict[date, dict] = {row["date"]: row for row in by_day}
        data = []
        start_date = (timezone.now() - timedelta(days=days - 1)).date()
        today = timezone.now().date()
        current = start_date
        while current <= today:
            if current in data_map:
                row = data_map[current]
                data.append(
                    {
                        "date": current,
                        "visits": row["visits"],
                        "unique_visitors": row["unique_visitors"],
                    }
                )
            else:
                data.append({"date": current, "visits": 0, "unique_visitors": 0})
            current += timedelta(days=1)

        totals = visits_qs.aggregate(
            total_visits=Count("id"),
            unique_visitors=Count("session_id", distinct=True),
        )

        return Response(
            {
                "days": days,
                "total_visits": totals["total_visits"] or 0,
                "unique_visitors": totals["unique_visitors"] or 0,
                "data": data,
            }
        )


# ---------------------------------------------------------------------------
# View: AnalyticsBreakdownView  (authenticated)
# ---------------------------------------------------------------------------

class AnalyticsBreakdownView(APIView):
    """
    Return top pages, referrers, device breakdown, and country breakdown.
    Query params:
      days (int, default=30)
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "days",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Number of days to include (default 30, max 365)",
            )
        ],
        responses=AnalyticsBreakdownSerializer,
        description="Traffic source, page, device, and geographic breakdowns.",
        tags=["Analytics - Dashboard"],
    )
    def get(self, request):
        try:
            site = request.user.site
        except Site.DoesNotExist:
            return Response({"error": "Site not found."}, status=status.HTTP_404_NOT_FOUND)

        days = _parse_days(request)
        since = timezone.now() - timedelta(days=days)
        visits_qs = SiteVisit.objects.filter(site=site, timestamp__gte=since)

        # Top pages (limit 10)
        top_pages = (
            visits_qs.values("path")
            .annotate(visits=Count("id"))
            .order_by("-visits")[:10]
        )

        # Top referrer domains (limit 10, exclude empty)
        top_referrers = (
            visits_qs.exclude(referrer_domain="")
            .values("referrer_domain")
            .annotate(visits=Count("id"))
            .order_by("-visits")[:10]
        )

        # Device breakdown
        devices = (
            visits_qs.values("device")
            .annotate(visits=Count("id"))
            .order_by("-visits")
        )

        # Country breakdown (limit 20, exclude empty)
        countries = (
            visits_qs.exclude(country="")
            .values("country")
            .annotate(visits=Count("id"))
            .order_by("-visits")[:20]
        )

        return Response(
            {
                "days": days,
                "top_pages": [
                    {"path": row["path"], "visits": row["visits"]}
                    for row in top_pages
                ],
                "top_referrers": [
                    {"domain": row["referrer_domain"], "visits": row["visits"]}
                    for row in top_referrers
                ],
                "devices": [
                    {"device": row["device"], "visits": row["visits"]}
                    for row in devices
                ],
                "countries": [
                    {"country": row["country"], "visits": row["visits"]}
                    for row in countries
                ],
            }
        )
