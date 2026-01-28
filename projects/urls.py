"""
URL configuration for projects app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from projects.views import (
    DashboardProjectViewSet, DashboardProjectMediaViewSet,
    PublicProjectListView, PublicProjectDetailView,
    ExternalProjectViewSet
)

# Dashboard router
dashboard_router = DefaultRouter()
dashboard_router.register(r'projects', DashboardProjectViewSet, basename='dashboard-projects')
dashboard_router.register(r'media', DashboardProjectMediaViewSet, basename='dashboard-media')

# External router
external_router = DefaultRouter()
external_router.register(r'', ExternalProjectViewSet, basename='external-projects')

# URL patterns
urlpatterns = [
    # Dashboard URLs
    path('dashboard/', include(dashboard_router.urls)),
    
    # Public URLs
    path('public/', PublicProjectListView.as_view(), name='public-projects'),
    path('public/<slug:slug>/', PublicProjectDetailView.as_view(), name='public-project-detail'),
    
    # External API URLs
    path('external/', include(external_router.urls)),
]
