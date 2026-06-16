from django.core.management.base import BaseCommand
from billing.models import Plan, PlanPrice, PaymentProvider
from decimal import Decimal

class Command(BaseCommand):
    help = 'Seeds initial billing plans and payment providers'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding plans and payment providers...")

        # 1. Payment Providers
        PaymentProvider.objects.update_or_create(
            name="polar",
            defaults={
                "is_enabled": True,
                "display_label": "Pay with Polar (USD)",
                "description": "Secure credit card payments via Polar."
            }
        )
        PaymentProvider.objects.update_or_create(
            name="bkash",
            defaults={
                "is_enabled": True,
                "display_label": "Pay with Bkash (BDT)",
                "description": "Local mobile money payments via Bkash."
            }
        )

        # 2. Plans
        # Free
        free_plan, _ = Plan.objects.update_or_create(
            tier="free",
            defaults={
                "name": "Free",
                "max_sites": 1,
                "max_projects": 10,
                "max_blogs": 10,
                "max_team_members": 1,
                "allow_custom_domain": False,
                "allow_remove_branding": False,
                "allow_api_access": False,
                "allow_full_analytics": False,
                "allow_all_templates": False,
                "allow_priority_support": False,
            }
        )

        # Pro
        pro_plan, _ = Plan.objects.update_or_create(
            tier="pro",
            defaults={
                "name": "Pro",
                "max_sites": 3,
                "max_projects": -1,
                "max_blogs": -1,
                "max_team_members": 1,
                "allow_custom_domain": True,
                "allow_remove_branding": True,
                "allow_api_access": False,
                "allow_full_analytics": False,
                "allow_all_templates": False,
                "allow_priority_support": False,
            }
        )

        # Team
        team_plan, _ = Plan.objects.update_or_create(
            tier="team",
            defaults={
                "name": "Team",
                "max_sites": 10,
                "max_projects": -1,
                "max_blogs": -1,
                "max_team_members": 10,
                "allow_custom_domain": True,
                "allow_remove_branding": True,
                "allow_api_access": True,
                "allow_full_analytics": True,
                "allow_all_templates": True,
                "allow_priority_support": True,
                "base_seats_included": 3,
                "price_per_extra_seat_usd": Decimal("8.00"),
                "price_per_extra_seat_bdt": Decimal("399.00"),
            }
        )

        # 3. Plan Prices
        prices = [
            (pro_plan, "monthly", "polar", "USD", Decimal("9.00")),
            (pro_plan, "annual", "polar", "USD", Decimal("90.00")),
            (pro_plan, "monthly", "bkash", "BDT", Decimal("490.00")),
            (pro_plan, "annual", "bkash", "BDT", Decimal("4990.00")),
            (team_plan, "monthly", "polar", "USD", Decimal("29.00")),
            (team_plan, "annual", "polar", "USD", Decimal("290.00")),
            (team_plan, "monthly", "bkash", "BDT", Decimal("1490.00")),
            (team_plan, "annual", "bkash", "BDT", Decimal("14990.00")),
        ]

        for plan, interval, provider, currency, amount in prices:
            PlanPrice.objects.update_or_create(
                plan=plan,
                interval=interval,
                provider=provider,
                currency=currency,
                defaults={
                    "amount": amount,
                    "is_active": True
                }
            )

        from billing.models import PromotionCampaign
        from datetime import datetime, timezone

        # 4. Promotion Campaigns
        sept_30_2026 = datetime(2026, 9, 30, 23, 59, 59, tzinfo=timezone.utc)
        
        PromotionCampaign.objects.update_or_create(
            name="Founding Member Promotion",
            defaults={
                "plan_granted": pro_plan,
                "duration_days": 180,
                "valid_until": sept_30_2026,
                "auto_apply_on_signup": True,
                "is_active": True
            }
        )

        self.stdout.write(self.style.SUCCESS('Successfully seeded plans and payment providers.'))
