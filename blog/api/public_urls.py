"""
Public API URLs for blog posts.
Domain-based access for published content.
"""
from django.urls import path
from blog.api.public_views import (
    PublicBlogPostListView,
    PublicBlogPostDetailView,
    PublicBlogPostCommentsView,
    PublicBlogTagsView,
    PublicBlogCategoriesView,
)

urlpatterns = [
    path('blog/', PublicBlogPostListView.as_view(), name='public-blog-list'),
    path('blog/<slug:slug>/', PublicBlogPostDetailView.as_view(), name='public-blog-detail'),
    path('blog/<slug:slug>/comments/', PublicBlogPostCommentsView.as_view(), name='public-blog-comments'),
    path('blog/tags/', PublicBlogTagsView.as_view(), name='public-blog-tags'),
    path('blog/categories/', PublicBlogCategoriesView.as_view(), name='public-blog-categories'),
]
