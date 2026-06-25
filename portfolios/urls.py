"""
URL configuration for portfolios app - Dashboard routes.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from portfolios.views import (
    DashboardSiteView,
    CustomDomainViewSet,
    TemplateConfigView,
    MigrationLogListView,
    SiteSEOView,
)

router = DefaultRouter()
router.register(r'custom-domains', CustomDomainViewSet, basename='custom-domain')

urlpatterns = [
    path('site/', DashboardSiteView.as_view(), name='dashboard-site'),
    path('site/seo/', SiteSEOView.as_view(), name='dashboard-site-seo'),
    # Template config endpoints (singleton per user — GET + PATCH only, no PUT/DELETE)
    path('template-config/', TemplateConfigView.as_view(), name='template-config'),
    path('template-config/migration-logs/', MigrationLogListView.as_view(), name='template-config-migration-logs'),
    path('', include(router.urls)),
]
