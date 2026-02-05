"""
Public API URL configuration for experiences app.
"""
from rest_framework.routers import DefaultRouter
from experiences.views import (
    PublicExperienceViewSet, 
    PublicSkillViewSet,
    PublicSocialLinkViewSet
)

router = DefaultRouter()
router.register(r'experiences', PublicExperienceViewSet, basename='public-experiences')
router.register(r'skills', PublicSkillViewSet, basename='public-skills')
router.register(r'social-links', PublicSocialLinkViewSet, basename='public-social-links')

urlpatterns = router.urls
