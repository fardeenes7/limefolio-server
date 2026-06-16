from django.contrib import admin
from .models import (
    Plan, PlanPrice, PaymentProvider, Subscription, 
    Invoice, PromoCode, UserBalance, BalanceTransaction,
    PromotionCampaign
)

@admin.register(PromotionCampaign)
class PromotionCampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'plan_granted', 'duration_days', 'valid_until', 'is_active', 'auto_apply_on_signup')
    list_filter = ('is_active', 'auto_apply_on_signup')
    search_fields = ('name', 'claim_code')

class PlanPriceInline(admin.TabularInline):
    model = PlanPrice
    extra = 1

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("name", "tier", "is_active", "created_at")
    list_filter = ("is_active", "tier")
    inlines = [PlanPriceInline]

@admin.register(PaymentProvider)
class PaymentProviderAdmin(admin.ModelAdmin):
    list_display = ("name", "is_enabled", "display_label", "updated_at")
    list_filter = ("is_enabled",)

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "provider", "status", "current_period_end")
    list_filter = ("status", "provider", "plan")
    search_fields = ("user__username", "user__email", "provider_subscription_id")

@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ("code", "discount_type", "discount_value", "is_active", "uses_count", "max_uses")
    list_filter = ("is_active", "discount_type", "currency")
    search_fields = ("code",)

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "provider", "amount_charged", "currency", "status", "created_at")
    list_filter = ("status", "provider", "currency")
    search_fields = ("user__username", "user__email", "provider_invoice_id", "bkash_payment_id")

@admin.register(UserBalance)
class UserBalanceAdmin(admin.ModelAdmin):
    list_display = ("user", "amount_usd", "updated_at")
    search_fields = ("user__username", "user__email")

@admin.register(BalanceTransaction)
class BalanceTransactionAdmin(admin.ModelAdmin):
    list_display = ("user", "type", "amount_usd", "created_at")
    list_filter = ("type",)
    search_fields = ("user__username", "user__email")
