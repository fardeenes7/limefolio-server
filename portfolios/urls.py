"""
URL configuration for portfolios app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from portfolios.views import DashboardSiteViewSet, PublicSiteDetailView

# Dashboard router
dashboard_router = DefaultRouter()
dashboard_router.register(r'', DashboardSiteViewSet, basename='dashboard-site')

# URL patterns
urlpatterns = [
    # Dashboard URLs
    path('dashboard/', include(dashboard_router.urls)),
    
    # Public URLs
    path('public/', PublicSiteDetailView.as_view(), name='public-site'),
]
