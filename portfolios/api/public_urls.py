"""
Public URL configuration for portfolios app.
"""
from django.urls import path
from portfolios.views import PublicSiteDetailView

urlpatterns = [
    path('', PublicSiteDetailView.as_view(), name='public-site'),
]
