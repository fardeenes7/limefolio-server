"""
Public URL configuration for projects app.
"""
from django.urls import path
from projects.views import PublicProjectListView, PublicProjectDetailView

urlpatterns = [
    path('projects/', PublicProjectListView.as_view(), name='public-projects'),
    path('projects/<slug:slug>/', PublicProjectDetailView.as_view(), name='public-project-detail'),
]
