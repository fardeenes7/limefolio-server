from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import AnonymousUser
from portfolios.models import Site, CustomDomain
from core.models import APIKey


class DomainBasedAuthentication(BaseAuthentication):
    """
    Authenticates requests based on Host header.
    Extracts subdomain or custom domain and finds associated Site.
    Returns AnonymousUser but attaches site to request.
    Used for public site API endpoints.
    """
    
    def authenticate(self, request):
        host = request.get_host().split(':')[0]  # Remove port if present
        site = self._get_site_from_host(host)
        
        if site:
            request.site = site
            # Return AnonymousUser for public access
            return (AnonymousUser(), None)
        
        # No site found, let other authenticators try
        return None
    
    def _get_site_from_host(self, host):
        """Extract site from subdomain or custom domain"""
        
        # Check if it's a subdomain (*.limefolio.com)
        if host.endswith('.limefolio.com'):
            subdomain = host.replace('.limefolio.com', '')
            return Site.objects.filter(subdomain=subdomain, is_active=True).first()
        
        # Check custom domains
        custom_domain = CustomDomain.objects.filter(
            domain=host,
            status='verified'
        ).select_related('site').first()
        
        if custom_domain:
            return custom_domain.site
        
        return None


class APIKeyAuthentication(BaseAuthentication):
    """
    Authenticates using X-API-Key and X-API-Secret headers.
    Validates key/secret pair and attaches site to request.
    Used for external/programmatic API access.
    """
    
    def authenticate(self, request):
        api_key = request.META.get('HTTP_X_API_KEY')
        api_secret = request.META.get('HTTP_X_API_SECRET')
        
        if not api_key or not api_secret:
            return None
        
        try:
            api_key_obj = APIKey.objects.select_related('site').get(
                key=api_key,
                is_active=True
            )
        except APIKey.DoesNotExist:
            raise AuthenticationFailed('Invalid API key')
        
        # Verify secret
        if not api_key_obj.verify_secret(api_secret):
            raise AuthenticationFailed('Invalid API secret')
        
        # Check rate limit
        if api_key_obj.is_rate_limited():
            raise AuthenticationFailed('Rate limit exceeded. Try again later.')
        
        # Increment request count
        api_key_obj.increment_request_count()
        
        # Attach API key and site to request
        request.api_key = api_key_obj
        request.site = api_key_obj.site
        
        # Return site owner as the authenticated user
        return (api_key_obj.site.user, None)
    
    def authenticate_header(self, request):
        return 'X-API-Key'
