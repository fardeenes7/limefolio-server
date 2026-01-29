"""
External API URL configuration for experiences app.
"""
from rest_framework.routers import DefaultRouter
from experiences.views import ExternalExperienceViewSet, ExternalSocialLinkViewSet

router = DefaultRouter()
router.register(r'experiences', ExternalExperienceViewSet, basename='external-experiences')
router.register(r'social-links', ExternalSocialLinkViewSet, basename='external-social-links')

urlpatterns = router.urls
