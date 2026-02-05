"""
External API URL configuration for experiences app.
"""
from rest_framework.routers import DefaultRouter
from experiences.views import (
    ExternalExperienceViewSet, 
    ExternalSkillViewSet,
    ExternalSocialLinkViewSet
)

router = DefaultRouter()
router.register(r'experiences', ExternalExperienceViewSet, basename='external-experiences')
router.register(r'skills', ExternalSkillViewSet, basename='external-skills')
router.register(r'social-links', ExternalSocialLinkViewSet, basename='external-social-links')

urlpatterns = router.urls
