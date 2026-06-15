"""
URL configuration for portfolios app - Dashboard routes.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from portfolios.views import DashboardSiteView, CustomDomainViewSet

router = DefaultRouter()
router.register(r'custom-domains', CustomDomainViewSet, basename='custom-domain')

urlpatterns = [
    path('site/', DashboardSiteView.as_view(), name='dashboard-site'),
    path('', include(router.urls)),
]
