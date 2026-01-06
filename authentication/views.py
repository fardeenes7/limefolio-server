from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User


class GoogleLogin(SocialLoginView):
    """Google OAuth2 login view"""
    adapter_class = GoogleOAuth2Adapter
    permission_classes = [AllowAny]


class GitHubLogin(SocialLoginView):
    """GitHub OAuth2 login view"""
    adapter_class = GitHubOAuth2Adapter
    permission_classes = [AllowAny]


@api_view(['POST'])
@permission_classes([AllowAny])
def social_token_exchange(request):
    """
    Exchange social provider access token for JWT tokens
    
    Expected payload:
    {
        "provider": "google" or "github",
        "access_token": "provider_access_token"
    }
    
    Returns:
    {
        "access": "jwt_access_token",
        "refresh": "jwt_refresh_token",
        "user": {user_data}
    }
    """
    provider = request.data.get('provider')
    access_token = request.data.get('access_token')
    
    if not provider or not access_token:
        return Response(
            {'error': 'Provider and access_token are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate provider
    if provider not in ['google', 'github']:
        return Response(
            {'error': 'Invalid provider. Must be "google" or "github"'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Use the appropriate social login view
        if provider == 'google':
            view = GoogleLogin.as_view()
        else:
            view = GitHubLogin.as_view()
        
        # Create a new request with the access token
        request.data['access_token'] = access_token
        response = view(request._request)
        
        return Response(response.data, status=response.status_code)
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token_view(request):
    """
    Refresh JWT access token using refresh token
    
    Expected payload:
    {
        "refresh": "refresh_token"
    }
    
    Returns:
    {
        "access": "new_access_token",
        "refresh": "new_refresh_token"  # if ROTATE_REFRESH_TOKENS is True
    }
    """
    refresh_token = request.data.get('refresh')
    
    if not refresh_token:
        return Response(
            {'error': 'Refresh token is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        refresh = RefreshToken(refresh_token)
        data = {
            'access': str(refresh.access_token),
        }
        
        # If ROTATE_REFRESH_TOKENS is True, return new refresh token
        if hasattr(refresh, 'rotate'):
            refresh.rotate()
            data['refresh'] = str(refresh)
        
        return Response(data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': 'Invalid or expired refresh token'},
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['POST'])
def logout_view(request):
    """
    Logout user by blacklisting refresh token
    
    Expected payload:
    {
        "refresh": "refresh_token"
    }
    """
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        return Response(
            {'message': 'Successfully logged out'},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
def user_profile(request):
    """Get current user profile"""
    from authentication.serializers import UserSerializer
    
    serializer = UserSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)
