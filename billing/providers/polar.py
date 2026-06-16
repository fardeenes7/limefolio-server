from polar_sdk import Polar
from django.conf import settings
from decimal import Decimal

# Initialize Polar client
polar = Polar(
    access_token=settings.POLAR_ACCESS_TOKEN,
    server=settings.POLAR_ENVIRONMENT
)

def create_checkout_session(user, plan_price, promo_code=None, balance_to_use=Decimal("0.00")):
    """
    Creates a Polar checkout session.
    Returns {"checkout_url": str, "session_id": str}
    """
    # For a real implementation, you would calculate discount and pass metadata.
    # Polar handles actual checkout differently in its latest API (e.g. creating checkout links).
    # Since we need provider_price_id, we will assume plan_price.provider_price_id is valid.
    
    # In standard usage with polar-sdk:
    # res = polar.checkouts.create(...)
    
    # We will mock the Polar Checkout call based on the SDK.
    # Note: Polar API for checkouts varies; assuming standard product/price checkout.
    
    price_id = plan_price.provider_price_id
    if not price_id:
        raise ValueError("PlanPrice does not have a provider_price_id configured.")

    try:
        response = polar.checkouts.create(
            product_price_id=price_id,
            success_url=f"{settings.FRONTEND_URL}/dashboard/billing?success=true&session_id={{CHECKOUT_SESSION_ID}}",
            customer_email=user.email,
            customer_name=user.username,
            metadata={
                "user_id": str(user.id),
                "plan_price_id": str(plan_price.id),
                "promo_code_id": str(promo_code.id) if promo_code else "",
            }
        )
        return {
            "checkout_url": response.url,
            "session_id": response.id
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise e

def cancel_subscription(provider_subscription_id: str):
    """Cancels subscription at period end. Returns True on success."""
    try:
        polar.subscriptions.update(
            id=provider_subscription_id,
            cancel_at_period_end=True
        )
        return True
    except Exception:
        return False

def upgrade_subscription(provider_subscription_id: str, new_price_id: str):
    """Upgrades/downgrades subscription. Polar handles proration."""
    try:
        polar.subscriptions.update(
            id=provider_subscription_id,
            product_price_id=new_price_id,
            proration_behavior="prorate"
        )
        return True
    except Exception:
        return False

def get_subscription(provider_subscription_id: str):
    """Fetches current subscription state from Polar."""
    return polar.subscriptions.get(id=provider_subscription_id)
