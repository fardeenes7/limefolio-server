"""
URL configuration for portfolios app - Dashboard routes.
"""
from rest_framework.routers import DefaultRouter
from portfolios.views import DashboardSiteViewSet

router = DefaultRouter()
router.register(r'sites', DashboardSiteViewSet, basename='dashboard-sites')

urlpatterns = router.urls
