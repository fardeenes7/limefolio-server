"""
Public URL configuration for portfolios app.
"""
from django.urls import path
from portfolios.views import PublicSiteDetailView, PublicTemplateConfigView

urlpatterns = [
    path('', PublicSiteDetailView.as_view(), name='public-site'),
    path('template-config/', PublicTemplateConfigView.as_view(), name='public-template-config'),
]
