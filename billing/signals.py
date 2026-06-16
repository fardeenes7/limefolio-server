from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import PromotionCampaign, Subscription

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def auto_apply_promotions(sender, instance, created, **kwargs):
    if not created:
        return
        
    now = timezone.now()
    
    # Find any active campaign with auto_apply_on_signup=True
    campaigns = PromotionCampaign.objects.filter(
        is_active=True,
        auto_apply_on_signup=True
    )
    
    for campaign in campaigns:
        # Check date validity
        if campaign.valid_from and now < campaign.valid_from:
            continue
        if campaign.valid_until and now > campaign.valid_until:
            continue
            
        # Apply the first matching campaign
        Subscription.objects.create(
            user=instance,
            plan=campaign.plan_granted,
            provider="internal",
            status="active",
            current_period_start=now,
            current_period_end=now + timedelta(days=campaign.duration_days)
        )
        break # Apply only one
