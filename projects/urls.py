"""
URL configuration for projects app - Dashboard routes.
"""
from rest_framework.routers import DefaultRouter
from projects.views import DashboardProjectViewSet, DashboardProjectMediaViewSet

router = DefaultRouter()
router.register(r'projects', DashboardProjectViewSet, basename='dashboard-projects')
router.register(r'project-media', DashboardProjectMediaViewSet, basename='dashboard-project-media')

urlpatterns = router.urls
