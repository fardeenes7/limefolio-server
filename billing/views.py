from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from .models import Plan, PaymentProvider, PlanPrice, Invoice, PromoCode, UserBalance, BalanceTransaction
from .serializers import PlanSerializer, UserBalanceSerializer
from django.conf import settings
from standardwebhooks.webhooks import Webhook
from django.utils import timezone
from decimal import Decimal
import json

from .providers import polar as polar_provider
from .providers import bkash as bkash_provider
from .promo_utils import validate_promo_code, apply_promo_and_balance
from datetime import timedelta
from django.shortcuts import redirect

class PlanListView(APIView):

    permission_classes = [AllowAny]

    def get(self, request):
        enabled_providers = list(PaymentProvider.objects.filter(is_enabled=True).values_list('name', flat=True))
        
        # We fetch active plans
        plans = Plan.objects.filter(is_active=True).prefetch_related('prices')
        
        serializer = PlanSerializer(plans, many=True)
        data = serializer.data
        
        # Filter prices to only include enabled providers
        for plan_data in data:
            plan_data['prices'] = [
                price for price in plan_data['prices']
                if price['provider'] in enabled_providers
            ]
            
        return Response(data)

class PolarWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        payload = request.body
        headers = request.META

        webhook_headers = {
            "webhook-id": headers.get("HTTP_WEBHOOK_ID"),
            "webhook-timestamp": headers.get("HTTP_WEBHOOK_TIMESTAMP"),
            "webhook-signature": headers.get("HTTP_WEBHOOK_SIGNATURE"),
        }

        try:
            wh = Webhook(settings.POLAR_WEBHOOK_SECRET)
            event = wh.verify(payload, webhook_headers)
        except Exception as e:
            return Response({"error": "Invalid signature"}, status=status.HTTP_400_BAD_REQUEST)

        # We return 200 immediately and should process async, but doing sync here for simplicity.
        event_type = event.get("type")
        data = event.get("data", {})

        from .models import Subscription, Invoice
        from django.contrib.auth import get_user_model
        User = get_user_model()

        if event_type == "subscription.created" or event_type == "subscription.updated":
            # Polar subscription objects
            metadata = data.get("metadata", {})
            user_id = metadata.get("user_id")
            plan_price_id = metadata.get("plan_price_id")
            
            if user_id and plan_price_id:
                try:
                    user = User.objects.get(id=user_id)
                    plan_price = PlanPrice.objects.get(id=plan_price_id)
                    sub, created = Subscription.objects.get_or_create(
                        user=user,
                        defaults={
                            "plan": plan_price.plan,
                            "plan_price": plan_price,
                            "provider": "polar",
                            "status": "active",
                            "provider_subscription_id": data.get("id"),
                            "provider_customer_id": data.get("customer_id")
                        }
                    )
                    sub.status = "active"
                    sub.plan = plan_price.plan
                    sub.plan_price = plan_price
                    sub.current_period_start = data.get("current_period_start")
                    sub.current_period_end = data.get("current_period_end")
                    sub.save()
                except Exception as e:
                    pass

        elif event_type == "subscription.canceled":
            sub_id = data.get("id")
            try:
                sub = Subscription.objects.get(provider_subscription_id=sub_id)
                sub.status = "cancelled"
                sub.cancelled_at = timezone.now()
                sub.save()
            except Subscription.DoesNotExist:
                pass

        elif event_type == "subscription.revoked":
            sub_id = data.get("id")
            try:
                sub = Subscription.objects.get(provider_subscription_id=sub_id)
                sub.status = "expired"
                sub.save()
            except Subscription.DoesNotExist:
                pass

        elif event_type == "order.created":
            metadata = data.get("metadata", {})
            user_id = metadata.get("user_id")
            if user_id:
                try:
                    user = User.objects.get(id=user_id)
                    # Create or update invoice
                    Invoice.objects.create(
                        user=user,
                        provider="polar",
                        status="paid",
                        amount_gross=Decimal(data.get("amount", 0)) / 100,
                        amount_charged=Decimal(data.get("amount", 0)) / 100,
                        currency=data.get("currency", "USD").upper(),
                        provider_invoice_id=data.get("id")
                    )
                except Exception:
                    pass

        elif event_type == "order.refunded":
            invoice_id = data.get("id")
            try:
                inv = Invoice.objects.get(provider_invoice_id=invoice_id)
                inv.status = "refunded"
                inv.save()
            except Invoice.DoesNotExist:
                pass

        return Response({"status": "ok"})


class PromoValidateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        code = request.data.get("code")
        plan_tier = request.data.get("plan_tier")
        interval = request.data.get("interval")
        provider = request.data.get("provider")
        currency = request.data.get("currency")
        
        if not all([code, plan_tier, interval, provider, currency]):
            return Response({"valid": False, "error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        valid, promo, error, _ = validate_promo_code(code, plan_tier, interval, provider, currency, request.user)
        
        if not valid:
            return Response({"valid": False, "error": error}, status=status.HTTP_400_BAD_REQUEST)

        # Get gross amount
        try:
            plan = Plan.objects.get(tier=plan_tier)
            plan_price = PlanPrice.objects.get(plan=plan, interval=interval, provider=provider, currency=currency)
        except (Plan.DoesNotExist, PlanPrice.DoesNotExist):
            return Response({"valid": False, "error": "Invalid plan or price configuration."}, status=status.HTTP_400_BAD_REQUEST)

        res = apply_promo_and_balance(plan_price.amount, currency, promo, Decimal("0.00"), provider, request.user)
        
        return Response({
            "valid": True,
            "discount_type": res["discount_type"],
            "discount_value": res["discount_value"],
            "gross_amount": plan_price.amount,
            "discount_amount": res["discount_amount"],
            "final_amount": res["final_amount"],
            "overage_to_balance": res["overage_to_balance"],
            "message": f"Promo code applied successfully."
        })

class BalanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            balance = request.user.balance
        except UserBalance.DoesNotExist:
            balance = UserBalance.objects.create(user=request.user, amount_usd=0)
            
        transactions = BalanceTransaction.objects.filter(user=request.user).order_by('-created_at')[:10]
        
        return Response({
            "amount_usd": balance.amount_usd,
            "transactions": [
                {
                    "type": t.type,
                    "amount_usd": t.amount_usd,
                    "reason": t.reason,
                    "created_at": t.created_at
                } for t in transactions
            ]
        })


class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        plan_tier = request.data.get("plan_tier")
        interval = request.data.get("interval")
        provider = request.data.get("provider")
        promo_code_str = request.data.get("promo_code")
        use_balance = request.data.get("use_balance", False)
        extra_seats = int(request.data.get("extra_seats", 0))

        # Validations
        try:
            plan = Plan.objects.get(tier=plan_tier, is_active=True)
            currency = "USD" if provider == "polar" else "BDT"
            plan_price = PlanPrice.objects.get(plan=plan, interval=interval, provider=provider, currency=currency, is_active=True)
            prov = PaymentProvider.objects.get(name=provider, is_enabled=True)
        except (Plan.DoesNotExist, PlanPrice.DoesNotExist, PaymentProvider.DoesNotExist):
            return Response({"error": "Invalid plan, provider, or interval."}, status=status.HTTP_400_BAD_REQUEST)

        promo_obj = None
        if promo_code_str:
            valid, promo_obj, error, _ = validate_promo_code(promo_code_str, plan_tier, interval, provider, currency, request.user)
            if not valid:
                return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

        balance_to_use = Decimal("0.00")
        if use_balance and provider == "polar":
            try:
                balance_to_use = request.user.balance.amount_usd
            except UserBalance.DoesNotExist:
                pass

        # Add seat cost
        gross_amount = plan_price.amount
        if plan_tier == "team" and extra_seats > 0:
            if provider == "polar":
                gross_amount += Decimal(extra_seats) * plan.price_per_extra_seat_usd
            else:
                gross_amount += Decimal(extra_seats) * plan.price_per_extra_seat_bdt

        res = apply_promo_and_balance(gross_amount, currency, promo_obj, balance_to_use, provider, request.user)
        final_amount = res["final_amount"]
        discount = res["discount_amount"]
        actual_balance_used = res["balance_used"]
        overage = res["overage_to_balance"]

        if provider == "polar":
            try:
                # call provider checkouts
                checkout_res = polar_provider.create_checkout_session(
                    user=request.user, 
                    plan_price=plan_price, 
                    promo_code=promo_obj, 
                    balance_to_use=actual_balance_used
                )
                
                # create pending invoice
                invoice = Invoice.objects.create(
                    user=request.user,
                    plan_price=plan_price,
                    provider="polar",
                    status="pending",
                    amount_gross=gross_amount,
                    discount_amount=discount,
                    amount_charged=final_amount,
                    currency=plan_price.currency,
                    balance_used=actual_balance_used,
                    promo_code=promo_obj,
                    provider_payment_intent_id=checkout_res["session_id"]
                )

                # Wait for order.created webhook to actually deduct balance and apply overage
                return Response({"checkout_url": checkout_res["checkout_url"]})
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        elif provider == "bkash":
            try:
                # Create pending invoice
                invoice = Invoice.objects.create(
                    user=request.user,
                    plan_price=plan_price,
                    provider="bkash",
                    status="pending",
                    amount_gross=gross_amount,
                    discount_amount=discount,
                    amount_charged=final_amount,
                    currency=plan_price.currency,
                    balance_used=actual_balance_used,
                    promo_code=promo_obj,
                    pending_expires_at=timezone.now() + timedelta(minutes=settings.BKASH_PAYMENT_TIMEOUT_MINUTES)
                )

                # We need backend URL for callback
                backend_url = f"{request.scheme}://{request.get_host()}"
                callback_url = f"{backend_url}/api/billing/bkash/callback/"

                bkash_res = bkash_provider.create_payment(
                    amount_bdt=float(final_amount),
                    invoice_id=str(invoice.id),
                    callback_url=callback_url
                )

                invoice.bkash_payment_id = bkash_res["payment_id"]
                invoice.save()

                return Response({"checkout_url": bkash_res["bkash_url"]})
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"error": "Unsupported provider"}, status=status.HTTP_400_BAD_REQUEST)

class BkashCallbackView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        payment_id = request.query_params.get("paymentID")
        status_param = request.query_params.get("status")
        
        frontend_checkout_url = f"{settings.FRONTEND_URL}/checkout"
        frontend_success_url = f"{settings.FRONTEND_URL}/dashboard/billing?success=true"

        if not payment_id:
            return redirect(f"{frontend_checkout_url}?error=invalid_callback")

        try:
            invoice = Invoice.objects.get(bkash_payment_id=payment_id)
        except Invoice.DoesNotExist:
            return redirect(f"{frontend_checkout_url}?error=invoice_not_found")

        if status_param == "success":
            try:
                res = bkash_provider.execute_payment(payment_id)
                if res.get("status") == "success":
                    invoice.status = "paid"
                    invoice.bkash_trx_id = res.get("trx_id")
                    invoice.save()

                    # Activate subscription
                    from .models import Subscription
                    sub, created = Subscription.objects.get_or_create(
                        user=invoice.user,
                        defaults={
                            "plan": invoice.plan_price.plan,
                            "plan_price": invoice.plan_price,
                            "provider": "bkash",
                            "status": "active",
                        }
                    )
                    sub.status = "active"
                    sub.plan = invoice.plan_price.plan
                    sub.plan_price = invoice.plan_price
                    
                    # Update periods
                    now = timezone.now()
                    if not sub.current_period_end or sub.current_period_end < now:
                        sub.current_period_start = now
                    else:
                        # extending
                        sub.current_period_start = sub.current_period_end
                    
                    # Add duration based on interval
                    if invoice.plan_price.interval == "monthly":
                        sub.current_period_end = sub.current_period_start + timedelta(days=30)
                    else:
                        sub.current_period_end = sub.current_period_start + timedelta(days=365)
                        
                    # Clear grace period/cancelled flags
                    sub.grace_period_end = None
                    sub.cancelled_at = None
                    sub.save()

                    return redirect(frontend_success_url)
                else:
                    invoice.status = "failed"
                    invoice.save()
                    return redirect(f"{frontend_checkout_url}?error=payment_failed")
            except Exception:
                invoice.status = "failed"
                invoice.save()
                return redirect(f"{frontend_checkout_url}?error=payment_failed")

        elif status_param == "failed":
            invoice.status = "failed"
            invoice.save()
            return redirect(f"{frontend_checkout_url}?error=payment_failed")
            
        elif status_param == "cancel":
            invoice.status = "expired"
            invoice.save()
            return redirect(f"{frontend_checkout_url}?error=payment_cancelled")

        return redirect(f"{frontend_checkout_url}?error=unknown")


class UpgradeSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        plan_tier = request.data.get("plan_tier")
        interval = request.data.get("interval")
        
        try:
            sub = Subscription.objects.get(user=request.user, provider="polar", status="active")
        except Subscription.DoesNotExist:
            return Response({"error": "No active Polar subscription found."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            plan = Plan.objects.get(tier=plan_tier, is_active=True)
            plan_price = PlanPrice.objects.get(plan=plan, interval=interval, provider="polar", is_active=True)
        except (Plan.DoesNotExist, PlanPrice.DoesNotExist):
            return Response({"error": "Invalid plan or interval."}, status=status.HTTP_400_BAD_REQUEST)

        success = polar_provider.upgrade_subscription(sub.provider_subscription_id, plan_price.provider_price_id)
        if success:
            return Response({"message": "Subscription upgrade initiated."})
        return Response({"error": "Failed to upgrade subscription."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CancelSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            sub = Subscription.objects.get(user=request.user, status__in=["active", "grace_period"])
        except Subscription.DoesNotExist:
            return Response({"error": "No active subscription found."}, status=status.HTTP_400_BAD_REQUEST)

        if sub.provider == "polar":
            success = polar_provider.cancel_subscription(sub.provider_subscription_id)
            if success:
                sub.cancelled_at = timezone.now()
                sub.save()
                return Response({"message": "Subscription cancelled."})
            return Response({"error": "Failed to cancel Polar subscription."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        elif sub.provider == "bkash":
            sub.cancelled_at = timezone.now()
            sub.save()
            return Response({"message": "Bkash subscription cancelled. It will not renew."})

        return Response({"error": "Unsupported provider."}, status=status.HTTP_400_BAD_REQUEST)

class ReactivateSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            sub = Subscription.objects.get(user=request.user, status="active", cancelled_at__isnull=False)
        except Subscription.DoesNotExist:
            return Response({"error": "No cancelled active subscription found."}, status=status.HTTP_400_BAD_REQUEST)

        if sub.provider == "polar":
            # Need polar.subscriptions.update(cancel_at_period_end=False)
            try:
                polar_provider.polar.subscriptions.update(
                    id=sub.provider_subscription_id,
                    cancel_at_period_end=False
                )
                sub.cancelled_at = None
                sub.save()
                return Response({"message": "Subscription reactivated."})
            except Exception as e:
                return Response({"error": "Failed to reactivate Polar subscription."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        elif sub.provider == "bkash":
            sub.cancelled_at = None
            sub.save()
            return Response({"message": "Subscription reactivated."})

        return Response({"error": "Unsupported provider."}, status=status.HTTP_400_BAD_REQUEST)

class BkashUpgradeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        plan_tier = request.data.get("plan_tier")
        interval = request.data.get("interval")
        
        try:
            sub = Subscription.objects.get(user=request.user, provider="bkash", status="active")
        except Subscription.DoesNotExist:
            return Response({"error": "No active Bkash subscription found."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            plan = Plan.objects.get(tier=plan_tier, is_active=True)
            plan_price = PlanPrice.objects.get(plan=plan, interval=interval, provider="bkash", is_active=True)
        except (Plan.DoesNotExist, PlanPrice.DoesNotExist):
            return Response({"error": "Invalid plan or interval."}, status=status.HTTP_400_BAD_REQUEST)

        now = timezone.now()
        if not sub.current_period_end or sub.current_period_end <= now:
             return Response({"error": "Cannot calculate mid-cycle for expired period."}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate remaining days
        remaining_delta = sub.current_period_end - now
        remaining_days = remaining_delta.days
        
        total_days = 30 if interval == "monthly" else 365
        
        # very simple prorata cost of new plan
        daily_rate = plan_price.amount / Decimal(total_days)
        delta_amount = daily_rate * Decimal(remaining_days)

        delta_amount = max(delta_amount, Decimal("10.00"))

        try:
            # Create pending invoice for delta
            invoice = Invoice.objects.create(
                user=request.user,
                plan_price=plan_price,
                provider="bkash",
                status="pending",
                amount_gross=delta_amount,
                amount_charged=delta_amount,
                currency="BDT",
                pending_expires_at=timezone.now() + timedelta(minutes=settings.BKASH_PAYMENT_TIMEOUT_MINUTES)
            )

            backend_url = f"{request.scheme}://{request.get_host()}"
            callback_url = f"{backend_url}/api/billing/bkash/callback/"

            bkash_res = bkash_provider.create_payment(
                amount_bdt=float(delta_amount),
                invoice_id=str(invoice.id),
                callback_url=callback_url
            )

            invoice.bkash_payment_id = bkash_res["payment_id"]
            invoice.save()

            return Response({"checkout_url": bkash_res["bkash_url"]})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SubscriptionDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            from .models import Subscription
            sub = Subscription.objects.get(user=request.user)
            from .serializers import SubscriptionSerializer
            return Response(SubscriptionSerializer(sub).data)
        except Subscription.DoesNotExist:
            return Response({"error": "No subscription found."}, status=status.HTTP_404_NOT_FOUND)

class ClaimPromotionView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        claim_code = request.data.get("claim_code")
        if not claim_code:
            return Response({"error": "claim_code is required."}, status=status.HTTP_400_BAD_REQUEST)
            
        from .models import PromotionCampaign, Subscription
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        
        try:
            campaign = PromotionCampaign.objects.get(
                claim_code=claim_code, 
                is_active=True
            )
        except PromotionCampaign.DoesNotExist:
            return Response({"error": "Invalid or inactive promotion code."}, status=status.HTTP_400_BAD_REQUEST)
            
        if campaign.valid_from and now < campaign.valid_from:
            return Response({"error": "This promotion has not started yet."}, status=status.HTTP_400_BAD_REQUEST)
            
        if campaign.valid_until and now > campaign.valid_until:
            return Response({"error": "This promotion has expired."}, status=status.HTTP_400_BAD_REQUEST)
            
        # Check if user already has an active subscription
        sub, created = Subscription.objects.get_or_create(user=request.user, defaults={
            "plan": campaign.plan_granted,
            "provider": "internal",
            "status": "active"
        })
        
        if not created and sub.status == "active" and sub.provider != "internal":
            return Response({"error": "You already have an active paid subscription."}, status=status.HTTP_400_BAD_REQUEST)
            
        # Apply the promotion
        sub.plan = campaign.plan_granted
        sub.provider = "internal"
        sub.status = "active"
        sub.current_period_start = now
        sub.current_period_end = now + timedelta(days=campaign.duration_days)
        sub.save()
        
        return Response({
            "message": f"Promotion applied successfully. You now have {campaign.plan_granted.name} access for {campaign.duration_days} days."
        })

class LatestPromotionView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        from .models import PromotionCampaign
        from .serializers import PromotionCampaignSerializer
        from django.utils import timezone
        
        now = timezone.now()
        campaign = PromotionCampaign.objects.filter(
            is_active=True,
            auto_apply_on_signup=True
        ).exclude(valid_until__lt=now).order_by('-created_at').first()
        
        if campaign:
            return Response(PromotionCampaignSerializer(campaign).data)
        return Response({}, status=status.HTTP_204_NO_CONTENT)


