"""
URL configuration for media app - Dashboard routes.
"""
from django.urls import path
from media.views import (
    DashboardMediaListView,
    DashboardMediaDetailView,
    DashboardMediaPresignedURLView,
    DashboardMediaUploadView,
    SetFeaturedMediaView,
)

urlpatterns = [
    path('media/', DashboardMediaListView.as_view(), name='dashboard-media-list'),
    path('media/<int:pk>/', DashboardMediaDetailView.as_view(), name='dashboard-media-detail'),
    path('media/<int:pk>/set-featured/', SetFeaturedMediaView.as_view(), name='dashboard-media-set-featured'),
    path('media/presigned-url/', DashboardMediaPresignedURLView.as_view(), name='dashboard-media-presigned-url'),
    path('media/upload/', DashboardMediaUploadView.as_view(), name='dashboard-media-upload'),
]
