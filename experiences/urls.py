"""
URL configuration for experiences app - Dashboard routes.
"""
from rest_framework.routers import DefaultRouter
from experiences.views import (
    DashboardExperienceViewSet, 
    DashboardSkillViewSet,
    DashboardSocialLinkViewSet
)

router = DefaultRouter()
router.register(r'experiences', DashboardExperienceViewSet, basename='dashboard-experiences')
router.register(r'skills', DashboardSkillViewSet, basename='dashboard-skills')
router.register(r'social-links', DashboardSocialLinkViewSet, basename='dashboard-social-links')

urlpatterns = router.urls
