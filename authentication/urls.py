from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from . import views

urlpatterns = [
    # dj-rest-auth endpoints (login, logout, password reset, etc.)
    path('', include('dj_rest_auth.urls')),
    
    # Registration endpoint
    path('registration/', include('dj_rest_auth.registration.urls')),
    
    # Social authentication
    path('social/google/', views.GoogleLogin.as_view(), name='google_login'),
    path('social/github/', views.GitHubLogin.as_view(), name='github_login'),
    path('social/token-exchange/', views.social_token_exchange, name='social_token_exchange'),
    
    # JWT token endpoints
    path('token/refresh/', views.refresh_token_view, name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # User profile
    path('user/', views.user_profile, name='user_profile'),
    
    # Logout
    path('logout/', views.logout_view, name='logout'),
]
