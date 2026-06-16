from rest_framework import serializers
from .models import Plan, PlanPrice, Subscription, Invoice, UserBalance, PromotionCampaign

class PlanPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanPrice
        fields = ["id", "interval", "currency", "provider", "amount"]

class PlanSerializer(serializers.ModelSerializer):
    prices = serializers.SerializerMethodField()

    class Meta:
        model = Plan
        fields = [
            "id", "name", "tier", "max_sites", "max_projects", "max_blogs",
            "max_team_members", "allow_custom_domain", "allow_remove_branding",
            "allow_api_access", "allow_full_analytics", "allow_all_templates",
            "allow_priority_support", "base_seats_included",
            "price_per_extra_seat_usd", "price_per_extra_seat_bdt", "prices"
        ]

    def get_prices(self, obj):
        active_prices = obj.prices.filter(is_active=True)
        return PlanPriceSerializer(active_prices, many=True).data

class SubscriptionSerializer(serializers.ModelSerializer):
    plan_tier = serializers.CharField(source="plan.tier", read_only=True)
    plan_name = serializers.CharField(source="plan.name", read_only=True)
    
    class Meta:
        model = Subscription
        fields = [
            "id", "plan_tier", "plan_name", "provider", "status", "extra_seats",
            "current_period_start", "current_period_end", "cancelled_at",
            "grace_period_end", "is_access_allowed", "total_seats"
        ]

class InvoiceSerializer(serializers.ModelSerializer):
    plan_name = serializers.CharField(source="plan_price.plan.name", read_only=True)
    
    class Meta:
        model = Invoice
        fields = [
            "id", "plan_name", "provider", "status", "amount_charged",
            "currency", "balance_used", "created_at"
        ]

class UserBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBalance
        fields = ["amount_usd", "updated_at"]

class PromotionCampaignSerializer(serializers.ModelSerializer):
    plan_name = serializers.CharField(source='plan_granted.name', read_only=True)
    class Meta:
        model = PromotionCampaign
        fields = ['id', 'name', 'duration_days', 'valid_until', 'auto_apply_on_signup', 'plan_name']
