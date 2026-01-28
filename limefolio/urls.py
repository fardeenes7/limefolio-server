"""api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # OAuth authentication
    path('api/auth/', include('drf_social_oauth2.urls', namespace='drf')),
    
    # Dashboard API - Requires Bearer token
    path('api/dashboard/', include('portfolio.api.dashboard.urls')),
    
    # Site API - Domain-based, public read
    path('api/site/', include('portfolio.api.site.urls')),
    
    # External API - Requires API key/secret
    path('v1/', include('portfolio.api.external.urls')),
    
    # User endpoint
    path('api/user/', include('portfolio.urls')),
]
