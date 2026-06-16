from django.db import models
from django.conf import settings
from decimal import Decimal

class Plan(models.Model):
    TIER_CHOICES = [("free", "Free"), ("pro", "Pro"), ("team", "Team")]

    name = models.CharField(max_length=50)           # "Free", "Pro", "Team"
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, unique=True)
    is_active = models.BooleanField(default=True)

    # Limits
    max_sites = models.IntegerField(default=1)
    max_projects = models.IntegerField(default=10)   # -1 = unlimited
    max_blogs = models.IntegerField(default=10)      # -1 = unlimited
    max_team_members = models.IntegerField(default=1)
    allow_custom_domain = models.BooleanField(default=False)
    allow_remove_branding = models.BooleanField(default=False)
    allow_api_access = models.BooleanField(default=False)
    allow_full_analytics = models.BooleanField(default=False)
    allow_all_templates = models.BooleanField(default=False)
    allow_priority_support = models.BooleanField(default=False)

    # Seat-based pricing delta (Team only)
    base_seats_included = models.IntegerField(default=1)   # seats included in base price
    price_per_extra_seat_usd = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    price_per_extra_seat_bdt = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class PlanPrice(models.Model):
    INTERVAL_CHOICES = [("monthly", "Monthly"), ("annual", "Annual")]
    CURRENCY_CHOICES = [("USD", "USD"), ("BDT", "BDT")]
    PROVIDER_CHOICES = [("polar", "Polar"), ("bkash", "Bkash"), ("internal", "Internal")]

    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name="prices")
    interval = models.CharField(max_length=10, choices=INTERVAL_CHOICES)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Provider-specific product/price IDs (set after creating products on provider dashboard)
    provider_product_id = models.CharField(max_length=255, blank=True)
    provider_price_id = models.CharField(max_length=255, blank=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("plan", "interval", "currency", "provider")
        
    def __str__(self):
        return f"{self.plan.name} - {self.amount} {self.currency} ({self.interval})"

class PaymentProvider(models.Model):
    PROVIDER_CHOICES = [("polar", "Polar"), ("bkash", "Bkash"), ("internal", "Internal")]

    name = models.CharField(max_length=20, choices=PROVIDER_CHOICES, unique=True)
    is_enabled = models.BooleanField(default=True)
    display_label = models.CharField(max_length=50)   # e.g. "Pay with Polar (USD)"
    description = models.CharField(max_length=255, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.display_label

class Subscription(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("cancelled", "Cancelled"),
        ("past_due", "Past Due"),
        ("pending", "Pending"),
        ("expired", "Expired"),
        ("grace_period", "Grace Period"),  # Bkash missed renewal — 7-day window
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscription")
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    plan_price = models.ForeignKey(PlanPrice, on_delete=models.PROTECT, null=True)
    provider = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    # Extra seats (Team plan)
    extra_seats = models.IntegerField(default=0)

    # Dates
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    grace_period_end = models.DateTimeField(null=True, blank=True)  # Bkash only

    # Provider references
    provider_subscription_id = models.CharField(max_length=255, blank=True)
    provider_customer_id = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_seats(self):
        return self.plan.base_seats_included + self.extra_seats

    @property
    def is_access_allowed(self):
        return self.status in ("active", "grace_period")
        
    def __str__(self):
        return f"{self.user.username} - {self.plan.name} ({self.status})"

class PromoCode(models.Model):
    DISCOUNT_TYPE_CHOICES = [("percentage", "Percentage"), ("fixed", "Fixed Amount")]
    CURRENCY_CHOICES = [("USD", "USD"), ("BDT", "BDT"), ("any", "Any")]

    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=5, choices=CURRENCY_CHOICES, default="any")

    # Restrictions
    applicable_plans = models.ManyToManyField(Plan, blank=True)  # empty = all plans
    max_uses = models.IntegerField(null=True, blank=True)         # null = unlimited
    uses_count = models.IntegerField(default=0)
    valid_from = models.DateTimeField(null=True, blank=True)
    valid_until = models.DateTimeField(null=True, blank=True)
    one_time_per_user = models.BooleanField(default=True)
    is_recurring = models.BooleanField(default=False)  # Applies every renewal or just first

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.code

class Invoice(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
        ("expired", "Expired"),
        ("refunded", "Refunded"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True)
    plan_price = models.ForeignKey(PlanPrice, on_delete=models.PROTECT, null=True)
    provider = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    amount_gross = models.DecimalField(max_digits=10, decimal_places=2)   # Before discount
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_charged = models.DecimalField(max_digits=10, decimal_places=2) # After discount
    currency = models.CharField(max_length=3)
    balance_used = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # USD balance applied

    promo_code = models.ForeignKey("PromoCode", on_delete=models.SET_NULL, null=True, blank=True)

    # Provider references
    provider_invoice_id = models.CharField(max_length=255, blank=True)
    provider_payment_intent_id = models.CharField(max_length=255, blank=True)

    # Bkash-specific
    bkash_payment_id = models.CharField(max_length=255, blank=True)
    bkash_trx_id = models.CharField(max_length=255, blank=True)
    pending_expires_at = models.DateTimeField(null=True, blank=True)  # 30-min timeout for Bkash

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class UserBalance(models.Model):
    """USD-only balance used at Polar checkout. Cannot be withdrawn."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="balance")
    amount_usd = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)

class BalanceTransaction(models.Model):
    TYPE_CHOICES = [("credit", "Credit"), ("debit", "Debit")]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    amount_usd = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.CharField(max_length=255)  # e.g. "Promo code SUMMER50 overage"
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class PromotionCampaign(models.Model):
    name = models.CharField(max_length=255)  # e.g., "Founding Member Promotion"
    plan_granted = models.ForeignKey(Plan, on_delete=models.CASCADE)
    
    # Duration of the free upgrade
    duration_days = models.IntegerField(default=180)  # e.g., 180 days for 6 months
    
    # Time window for the promotion
    valid_from = models.DateTimeField(null=True, blank=True)
    valid_until = models.DateTimeField(null=True, blank=True)
    
    # How it's applied
    auto_apply_on_signup = models.BooleanField(default=False)
    claim_code = models.CharField(max_length=50, blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

