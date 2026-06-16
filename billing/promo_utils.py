from decimal import Decimal
from django.utils import timezone
from .models import PromoCode, Invoice, UserBalance

def validate_promo_code(code_str, plan_tier, interval, provider, currency, user):
    """
    Returns (valid: bool, data: dict, error_message: str, promo_obj)
    """
    try:
        promo = PromoCode.objects.get(code=code_str, is_active=True)
    except PromoCode.DoesNotExist:
        return False, None, "Invalid or inactive promo code.", None

    now = timezone.now()
    if promo.valid_from and now < promo.valid_from:
        return False, None, "Promo code is not yet active.", None
    if promo.valid_until and now > promo.valid_until:
        return False, None, "Promo code has expired.", None

    if promo.max_uses is not None and promo.uses_count >= promo.max_uses:
        return False, None, "Promo code usage limit reached.", None

    if promo.currency != "any" and promo.currency != currency:
        return False, None, f"Promo code is only valid for {promo.currency} payments.", None

    if promo.applicable_plans.exists() and not promo.applicable_plans.filter(tier=plan_tier).exists():
        return False, None, "Promo code is not applicable for this plan.", None

    if promo.one_time_per_user:
        if Invoice.objects.filter(user=user, promo_code=promo, status__in=["paid", "pending"]).exists():
            return False, None, "You have already used this promo code.", None

    return True, promo, None, promo

def calculate_discount(gross_amount, promo_code):
    if not promo_code:
        return Decimal("0.00")
    if promo_code.discount_type == "percentage":
        discount = (gross_amount * promo_code.discount_value) / Decimal("100.00")
        return round(discount, 2)
    elif promo_code.discount_type == "fixed":
        return min(gross_amount, promo_code.discount_value)
    return Decimal("0.00")

def apply_promo_and_balance(gross_amount, currency, promo_code, balance_to_use, provider, user):
    discount = calculate_discount(gross_amount, promo_code)
    after_promo = gross_amount - discount
    overage = Decimal("0.00")

    if after_promo < 0:
        overage = abs(after_promo)
        after_promo = Decimal("0.00")

    after_balance = after_promo
    actual_balance_used = Decimal("0.00")

    if provider == "polar" and balance_to_use > 0:
        try:
            user_balance = user.balance.amount_usd
        except UserBalance.DoesNotExist:
            user_balance = Decimal("0.00")
            
        actual_balance_used = min(balance_to_use, after_promo, user_balance)
        after_balance = after_promo - actual_balance_used

    return {
        "final_amount": after_balance,
        "discount_amount": discount,
        "balance_used": actual_balance_used,
        "overage_to_balance": overage,
        "discount_type": promo_code.discount_type if promo_code else None,
        "discount_value": promo_code.discount_value if promo_code else Decimal("0.00")
    }
