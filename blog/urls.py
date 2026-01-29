from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BlogPostViewSet, BlogCommentViewSet

router = DefaultRouter()
router.register(r'posts', BlogPostViewSet, basename='blogpost')
router.register(r'comments', BlogCommentViewSet, basename='blogcomment')

urlpatterns = [
    path('', include(router.urls)),
]
