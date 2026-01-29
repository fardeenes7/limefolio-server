"""
Public API URLs for media.
Domain-based access for site media.
"""
from django.urls import path
from media.api.public_views import (
    PublicMediaListView,
    PublicMediaDetailView,
)

urlpatterns = [
    path('media/', PublicMediaListView.as_view(), name='public-media-list'),
    path('media/<int:id>/', PublicMediaDetailView.as_view(), name='public-media-detail'),
]
