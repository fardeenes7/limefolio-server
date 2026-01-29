"""
URL configuration for core app (API Keys).
"""
from rest_framework.routers import DefaultRouter
from core.views import DashboardAPIKeyViewSet

router = DefaultRouter()
router.register(r'api-keys', DashboardAPIKeyViewSet, basename='dashboard-api-keys')

urlpatterns = router.urls
