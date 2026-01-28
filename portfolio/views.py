from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class CurrentUserView(APIView):
    """Get current authenticated user with site information"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        site_data = None
        
        # Get site info if it exists
        if hasattr(user, 'site'):
            site_data = {
                'subdomain': user.site.subdomain,
                'title': user.site.title,
                'is_published': user.site.is_published,
                'uuid': str(user.site.uuid),
            }
        
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'site': site_data,
        })
