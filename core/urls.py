"""
URL configuration for core app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import DashboardAPIKeyViewSet

# Dashboard router
dashboard_router = DefaultRouter()
dashboard_router.register(r'', DashboardAPIKeyViewSet, basename='dashboard-api-keys')

# URL patterns
urlpatterns = [
    # Dashboard URLs
    path('dashboard/', include(dashboard_router.urls)),
]
