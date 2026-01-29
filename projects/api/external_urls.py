"""
External API URL configuration for projects app.
"""
from rest_framework.routers import DefaultRouter
from projects.views import ExternalProjectViewSet

router = DefaultRouter()
router.register(r'projects', ExternalProjectViewSet, basename='external-projects')

urlpatterns = router.urls
