from portfolios.models import Site, CustomDomain
#IMPORT debug from setting
from limefolio.settings import DEBUG

BASE_DOMAIN = 'limefolio.com' if DEBUG else 'localhost:3000' 

class SiteDetectionMiddleware:
    """
    Detects site from subdomain or custom domain.
    Attaches site object to request for all requests.
    This runs before authentication and makes site available globally.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # host = request.get_host().split(':')[0]  # Remove port
        host  = request.headers.get('X-Public-Domain')

        site = None


        if not host:
            return self.get_response(request)
            
        # Check if it's a subdomain (*.limefolio.com)
        if host.endswith(BASE_DOMAIN) or '.' not in host:
            subdomain = host.replace(f'.{BASE_DOMAIN}', '')
            site = Site.objects.filter(subdomain=subdomain, is_active=True).first()
        else:
            # Check custom domains
            custom_domain = CustomDomain.objects.filter(
                domain=host,
                status='verified'
            ).select_related('site').first()
            
            if custom_domain:
                site = custom_domain.site
        
        # Attach site to request (None if not found)
        request.site = site
        
        response = self.get_response(request)
        return response
