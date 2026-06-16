import requests
from django.conf import settings
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

def get_token() -> str:
    """
    Fetches a Bkash access token.
    Cache token in Django cache for its TTL duration.
    """
    token = cache.get('bkash_token')
    if token:
        return token

    url = f"{settings.BKASH_BASE_URL}/tokenized/checkout/token/grant"
    headers = {
        "username": settings.BKASH_USERNAME,
        "password": settings.BKASH_PASSWORD,
        "app_key": settings.BKASH_APP_KEY,
        "app_secret": settings.BKASH_APP_SECRET,
    }

    try:
        response = requests.post(url, json=headers)
        response.raise_for_status()
        data = response.json()
        token = data.get('id_token')
        expires_in = data.get('expires_in', 3600)
        cache.set('bkash_token', token, timeout=expires_in - 60)
        return token
    except Exception as e:
        logger.error(f"Bkash Token Error: {str(e)}")
        raise e

def create_payment(amount_bdt: float, invoice_id: str, callback_url: str) -> dict:
    """
    Creates a Bkash payment request.
    Returns {"bkash_url": str, "payment_id": str}
    invoice_id passed as merchantInvoiceNumber.
    """
    token = get_token()
    url = f"{settings.BKASH_BASE_URL}/tokenized/checkout/create"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "x-app-key": settings.BKASH_APP_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "mode": "0011",
        "payerReference": " ",
        "callbackURL": callback_url,
        "amount": str(amount_bdt),
        "currency": "BDT",
        "intent": "sale",
        "merchantInvoiceNumber": str(invoice_id)
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return {
            "bkash_url": data.get("bkashURL"),
            "payment_id": data.get("paymentID")
        }
    except Exception as e:
        logger.error(f"Bkash Create Payment Error: {str(e)}")
        raise e

def execute_payment(payment_id: str) -> dict:
    """
    Executes (confirms) a payment after user completes on Bkash side.
    Returns {"status": str, "trx_id": str}
    """
    token = get_token()
    url = f"{settings.BKASH_BASE_URL}/tokenized/checkout/execute"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "x-app-key": settings.BKASH_APP_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "paymentID": payment_id
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        
        status_code = data.get("statusCode")
        if status_code == "0000":
            return {"status": "success", "trx_id": data.get("trxID")}
        else:
            return {"status": "failed", "trx_id": None, "message": data.get("statusMessage")}
    except Exception as e:
        logger.error(f"Bkash Execute Payment Error: {str(e)}")
        raise e

def query_payment(payment_id: str) -> dict:
    """Queries payment status by payment_id."""
    token = get_token()
    url = f"{settings.BKASH_BASE_URL}/tokenized/checkout/payment/status"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "x-app-key": settings.BKASH_APP_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "paymentID": payment_id
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Bkash Query Payment Error: {str(e)}")
        raise e
