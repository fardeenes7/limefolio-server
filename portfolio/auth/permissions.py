from rest_framework import permissions


# New permission classes for multi-auth API

class HasValidAPIKey(permissions.BasePermission):
    """
    Permission class to check if request has valid API key/secret.
    Used for external API endpoints.
    """
    
    def has_permission(self, request, view):
        # Check if APIKeyAuthentication succeeded
        api_key = getattr(request, 'api_key', None)
        if not api_key:
            return False
        
        if not api_key.is_active:
            return False
        
        # Check read-only restriction
        if api_key.read_only and request.method not in permissions.SAFE_METHODS:
            return False
        
        return True


class IsPublicRead(permissions.BasePermission):
    """
    Allow public read access, require authentication for write operations.
    Used for site API endpoints (subdomain/custom domain).
    """
    
    def has_permission(self, request, view):
        # Allow all GET, HEAD, OPTIONS requests
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Require authentication for write operations
        return request.user and request.user.is_authenticated


class IsAuthenticatedDashboard(permissions.BasePermission):
    """
    Require OAuth2 Bearer token authentication.
    Used for dashboard API endpoints.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
