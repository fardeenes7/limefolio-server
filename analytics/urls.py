"""
URL configuration for the analytics app.
"""

from django.urls import path
from analytics.views import (
    TrackVisitView,
    DashboardStatsView,
    AnalyticsOverviewView,
    AnalyticsBreakdownView,
)

urlpatterns = [
    # POST — public, called by the portfolio frontend to record a page view
    path("track/", TrackVisitView.as_view(), name="analytics-track"),
    # GET — authenticated, all dashboard KPIs and recent content
    path("stats/", DashboardStatsView.as_view(), name="analytics-stats"),
    # GET — authenticated, daily time-series chart data
    path("overview/", AnalyticsOverviewView.as_view(), name="analytics-overview"),
    # GET — authenticated, top pages / referrers / devices / countries
    path("breakdown/", AnalyticsBreakdownView.as_view(), name="analytics-breakdown"),
]
