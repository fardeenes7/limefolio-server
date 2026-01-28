"""
Views for API keys - Dashboard management.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.models import APIKey
from core.serializers import APIKeySerializer


class DashboardAPIKeyViewSet(viewsets.ModelViewSet):
    """
    Dashboard API Key management.
    Users can create and manage API keys for their site.
    """
    serializer_class = APIKeySerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete']  # No PUT
    
    def get_queryset(self):
        return APIKey.objects.filter(site__user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(site=self.request.user.site)
    
    @action(detail=True, methods=['post'])
    def regenerate(self, request, pk=None):
        """Regenerate API key"""
        api_key = self.get_object()
        api_key.key = APIKey.generate_key()
        api_key.save()
        return Response({'key': api_key.key})
    
    @action(detail=True, methods=['post'])
    def reset_secret(self, request, pk=None):
        """Reset API secret"""
        api_key = self.get_object()
        new_secret = APIKey.generate_secret()
        api_key.secret_hash = APIKey.hash_secret(new_secret)
        api_key.save()
        return Response({'secret': new_secret})
