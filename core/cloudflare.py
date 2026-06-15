import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class CloudflareClient:
    """Client for interacting with Cloudflare Custom Hostnames for SaaS API"""
    
    @classmethod
    def get_headers(cls):
        return {
            "Authorization": f"Bearer {settings.CLOUDFLARE_API_TOKEN}",
            "Content-Type": "application/json"
        }
    
    @classmethod
    def is_configured(cls) -> bool:
        return bool(settings.CLOUDFLARE_API_TOKEN and settings.CLOUDFLARE_ZONE_ID)
        
    @classmethod
    def add_custom_hostname(cls, domain: str):
        """
        Adds a custom hostname to the Cloudflare zone.
        Returns the Cloudflare ID for the custom hostname if successful, else None.
        """
        if not cls.is_configured():
            logger.warning("Cloudflare is not configured. Skipping add_custom_hostname.")
            return None
            
        url = f"https://api.cloudflare.com/client/v4/zones/{settings.CLOUDFLARE_ZONE_ID}/custom_hostnames"
        payload = {
            "hostname": domain,
            "ssl": {
                "method": "http",
                "type": "dv"
            }
        }
        
        try:
            response = requests.post(url, headers=cls.get_headers(), json=payload)
            data = response.json()
            
            if response.status_code in [200, 201] and data.get("success"):
                return data["result"]["id"]
            else:
                logger.error(f"Cloudflare API Error: {data.get('errors')}")
                return None
        except Exception as e:
            logger.error(f"Exception calling Cloudflare API: {e}")
            return None

    @classmethod
    def delete_custom_hostname(cls, cloudflare_id: str) -> bool:
        """
        Deletes a custom hostname from the Cloudflare zone.
        """
        if not cls.is_configured() or not cloudflare_id:
            logger.warning("Cloudflare is not configured or ID missing. Skipping delete_custom_hostname.")
            return False
            
        url = f"https://api.cloudflare.com/client/v4/zones/{settings.CLOUDFLARE_ZONE_ID}/custom_hostnames/{cloudflare_id}"
        
        try:
            response = requests.delete(url, headers=cls.get_headers())
            data = response.json()
            
            if response.status_code == 200 and data.get("success"):
                return True
            else:
                logger.error(f"Cloudflare API Error: {data.get('errors')}")
                return False
        except Exception as e:
            logger.error(f"Exception calling Cloudflare API: {e}")
            return False

    @classmethod
    def get_custom_hostname(cls, cloudflare_id: str):
        """
        Gets details for a custom hostname to check status.
        """
        if not cls.is_configured() or not cloudflare_id:
            logger.warning("Cloudflare is not configured or ID missing. Skipping get_custom_hostname.")
            return None
            
        url = f"https://api.cloudflare.com/client/v4/zones/{settings.CLOUDFLARE_ZONE_ID}/custom_hostnames/{cloudflare_id}"
        
        try:
            response = requests.get(url, headers=cls.get_headers())
            data = response.json()
            
            if response.status_code == 200 and data.get("success"):
                return data["result"]
            else:
                logger.error(f"Cloudflare API Error: {data.get('errors')}")
                return None
        except Exception as e:
            logger.error(f"Exception calling Cloudflare API: {e}")
            return None
