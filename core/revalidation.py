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
    public_app_domain = getattr(settings, 'PUBLIC_APP_DOMAIN', None)
    base_url = f"https://public.{public_app_domain}"

    if not token or not base_url:
        logger.warning("Revalidation skipped: REVALIDATION_TOKEN or PUBLIC_APP_DOMAIN not configured.")
        return False

    url = f"{base_url.rstrip('/')}/api/revalidate"
    params = {
        "secret": token,
    }

    # replace .limefolio.com from tag or path if present
    if tag:
        params["tag"] = tag.replace(f".{public_app_domain}", "")
    elif path:
        params["path"] = path.replace(f".{public_app_domain}", "")
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
