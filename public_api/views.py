from django.http import JsonResponse
from django.core.management import call_command
from django.views import View

class RunMigrationsView(View):
    """Public endpoint to trigger database migrations.
    This view runs ``manage.py migrate`` without input and returns a JSON
    response indicating success or failure. It is deliberately lightweight
    and does not require authentication - use with caution in production.
    """

    def get(self, request, *args, **kwargs):
        try:
            # Run migrations silently
            call_command('migrate', '--noinput', verbosity=0)
            return JsonResponse({"status": "ok", "message": "Migrations applied"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

class DomainAskView(View):
    """
    Endpoint for Caddy's On-Demand TLS feature.
    Caddy makes a GET request here with `?domain=example.com`.
    We return 200 OK if the domain is allowed, or 403 Forbidden otherwise.
    """
    def get(self, request, *args, **kwargs):
        domain = request.GET.get('domain')
        
        if not domain:
            from django.http import HttpResponse
            return HttpResponse("Domain parameter missing", status=400)
            
        # Clean domain
        domain = domain.lower().strip()
        
        from portfolios.models import CustomDomain, Site
        from django.conf import settings
        from django.http import HttpResponse
        
        # Check CustomDomain table
        if CustomDomain.objects.filter(domain=domain).exists():
            return HttpResponse("Allowed", status=200)
            
        # Check if it's a subdomain of the platform domain
        base_domain = getattr(settings, 'PUBLIC_APP_DOMAIN', 'limefolio.com')
        base_suffix = f'.{base_domain}'
        
        if domain.endswith(base_suffix):
            subdomain = domain[:-len(base_suffix)]
            if Site.objects.filter(subdomain=subdomain).exists():
                return HttpResponse("Allowed", status=200)
            
        return HttpResponse("Forbidden", status=403)

