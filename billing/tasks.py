from celery import shared_task
from django.utils import timezone
from .models import Invoice, Subscription, Plan
import logging
from datetime import timedelta
from django.conf import settings

logger = logging.getLogger(__name__)

@shared_task
def expire_pending_bkash_invoices():
    """
    Run every 5 minutes.
    Find pending Invoices where pending_expires_at < now.
    Mark them expired. Do NOT downgrade subscription yet.
    """
    now = timezone.now()
    invoices = Invoice.objects.filter(
        provider="bkash", 
        status="pending", 
        pending_expires_at__lt=now
    )
    count = invoices.update(status="expired")
    if count > 0:
        logger.info(f"Expired {count} pending Bkash invoices.")

@shared_task
def send_bkash_renewal_reminders():
    """
    Run daily.
    Find active Bkash subscriptions expiring in RENEWAL_REMINDER_DAYS_BEFORE days.
    Send renewal email/notification with a link to /dashboard/billing/renew.
    """
    now = timezone.now()
    target_date = now + timedelta(days=settings.RENEWAL_REMINDER_DAYS_BEFORE)
    
    subs = Subscription.objects.filter(
        provider="bkash",
        status="active",
        current_period_end__date=target_date.date(),
        cancelled_at__isnull=True
    )
    
    for sub in subs:
        # Dummy email send logic
        logger.info(f"Sending renewal reminder to {sub.user.email} for subscription {sub.id}")
        # send_mail(...)

@shared_task
def expire_grace_period_subscriptions():
    """
    Run daily.
    Find subscriptions in grace_period where grace_period_end < now.
    Set status=expired. Downgrade user to Free plan.
    """
    now = timezone.now()
    subs = Subscription.objects.filter(
        status="grace_period",
        grace_period_end__lt=now
    )
    
    free_plan = Plan.objects.get(tier="free")
    
    for sub in subs:
        sub.status = "expired"
        sub.plan = free_plan
        # Keep plan_price as is or nullify it
        sub.save()
        logger.info(f"Expired grace period for subscription {sub.id}. Downgraded to free.")

@shared_task
def process_missed_renewals():
    """
    Run daily.
    Find active Bkash subscriptions that passed current_period_end.
    Put them in grace_period.
    """
    now = timezone.now()
    subs = Subscription.objects.filter(
        provider="bkash",
        status="active",
        current_period_end__lt=now
    )
    
    for sub in subs:
        if sub.cancelled_at:
            # If they explicitly cancelled, just expire
            sub.status = "expired"
            sub.plan = Plan.objects.get(tier="free")
        else:
            # Otherwise grace period
            sub.status = "grace_period"
            sub.grace_period_end = now + timedelta(days=settings.BILLING_GRACE_PERIOD_DAYS)
        sub.save()

@shared_task
def expire_internal_subscriptions():
    """
    Run daily.
    Find subscriptions where provider="internal" and current_period_end < now.
    Set status=expired. The system will automatically fall back to the Free plan.
    """
    now = timezone.now()
    subs = Subscription.objects.filter(
        provider="internal",
        status="active",
        current_period_end__lt=now
    )
    
    free_plan = Plan.objects.get(tier="free")
    
    for sub in subs:
        sub.status = "expired"
        sub.plan = free_plan
        sub.save()
        logger.info(f"Expired internal promotion for subscription {sub.id}. Downgraded to free.")
