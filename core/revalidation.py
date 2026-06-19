import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def revalidate_public_cache(tag=None, path=None):
    """
    Triggers Next.js cache revalidation for the public application.
    """
    # Try to get settings, fall back to None if not defined
    token = getattr(settings, 'REVALIDATION_TOKEN', None)
    base_url = getattr(settings, 'PUBLIC_APP_URL', None)

    if not token or not base_url:
        logger.warning("Revalidation skipped: REVALIDATION_TOKEN or PUBLIC_APP_URL not configured.")
        return False

    url = f"{base_url.rstrip('/')}/api/revalidate"
    params = {
        "secret": token,
    }

    if tag:
        params["tag"] = tag
    elif path:
        params["path"] = path
    else:
        logger.warning("Revalidation skipped: Neither tag nor path provided.")
        return False

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        logger.info(f"Successfully triggered revalidation for {tag or path}")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to trigger revalidation: {str(e)}")
        return False

def revalidate_site_tags(site, *tag_suffixes):
    """
    Revalidates multiple tag suffixes for a site across its subdomain and verified custom domains.
    Example: revalidate_site_tags(site, "site", "projects", f"project-{slug}")
    """
    # Construct list of all domains for this site (Next.js middleware strips the base domain)
    domains = [site.subdomain]
    
    # Add verified custom domains
    custom_domains = site.custom_domains.filter(status='verified').values_list('domain', flat=True)
    domains.extend(list(custom_domains))
    
    for domain in domains:
        for suffix in tag_suffixes:
            revalidate_public_cache(tag=f"{domain}-{suffix}")
