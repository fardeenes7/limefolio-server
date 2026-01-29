"""
URL configuration for projects app - Dashboard routes.
"""
from rest_framework.routers import DefaultRouter
from projects.views import DashboardProjectViewSet

router = DefaultRouter()
router.register(r'projects', DashboardProjectViewSet, basename='dashboard-projects')

urlpatterns = router.urls
