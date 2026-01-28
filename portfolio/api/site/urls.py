"""
Site API URLs - Domain-based, Public Read-Only
Serves portfolio data based on subdomain or custom domain
"""
from django.urls import path
from .views import SiteDetailView, SiteProjectListView, SiteProjectDetailView

urlpatterns = [
    path('', SiteDetailView.as_view(), name='site-detail'),
    path('projects/', SiteProjectListView.as_view(), name='site-projects'),
    path('projects/<slug:slug>/', SiteProjectDetailView.as_view(), name='site-project-detail'),
]
