from rest_framework import permissions


class IsSiteOwner(permissions.BasePermission):
    """
    Permission to only allow owners of a site to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request for GET, HEAD or OPTIONS
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the site
        # Handle different model types
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        elif hasattr(obj, 'site'):
            return obj.site.owner == request.user
        
        return False


class IsSiteOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of a site to edit it.
    Read-only access for everyone else.
    """
    
    def has_permission(self, request, view):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions require authentication
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        elif hasattr(obj, 'site'):
            return obj.site.owner == request.user
        
        return False


class IsAuthenticatedOwner(permissions.BasePermission):
    """
    Only authenticated users can create, and only owners can modify.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        elif hasattr(obj, 'site'):
            return obj.site.owner == request.user
        
        return False


class CanManageSite(permissions.BasePermission):
    """
    Check if user can manage a specific site (owner or collaborator in future).
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # For now, only owner can manage
        # In future, add collaborator logic here
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        elif hasattr(obj, 'site'):
            return obj.site.owner == request.user
        
        return False
