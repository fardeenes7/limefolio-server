"""
Models for the analytics app.

SiteVisit tracks individual page views on public portfolio sites.
Each record represents one page load by a visitor.
"""

from django.db import models


class SiteVisit(models.Model):
    """
    Tracks a single page view on a portfolio site.
    Populated by the public portfolio frontend calling POST /api/analytics/track/.
    """

    DEVICE_CHOICES = [
        ("desktop", "Desktop"),
        ("mobile", "Mobile"),
        ("tablet", "Tablet"),
        ("unknown", "Unknown"),
    ]

    site = models.ForeignKey(
        "portfolios.Site",
        on_delete=models.CASCADE,
        related_name="visits",
    )

    # What was visited
    path = models.CharField(
        max_length=500,
        help_text='Page path, e.g. "/" or "/projects/my-app"',
    )

    # Where they came from
    referrer = models.CharField(
        max_length=1000,
        blank=True,
        default="",
        help_text="Full referrer URL",
    )
    referrer_domain = models.CharField(
        max_length=253,
        blank=True,
        default="",
        help_text="Extracted referrer domain, e.g. github.com",
    )

    # Where they are
    country = models.CharField(
        max_length=2,
        blank=True,
        default="",
        help_text="ISO-3166 country code, e.g. BD",
    )

    # What they are using
    device = models.CharField(
        max_length=10,
        choices=DEVICE_CHOICES,
        default="unknown",
    )
    browser = models.CharField(
        max_length=50,
        blank=True,
        default="",
        help_text="Browser name, e.g. Chrome",
    )

    # Session tracking (for unique visitor counting)
    session_id = models.CharField(
        max_length=64,
        db_index=True,
        help_text="Anonymous session UUID, set by the public frontend",
    )

    # Timestamp
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["site", "-timestamp"]),
            models.Index(fields=["site", "path"]),
            models.Index(fields=["site", "session_id"]),
        ]

    def __str__(self):
        return f"{self.site.subdomain} — {self.path} at {self.timestamp:%Y-%m-%d %H:%M}"
