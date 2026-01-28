from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_site(sender, instance, created, **kwargs):
    """Auto-create Site when a new user is created via OAuth"""
    if created:
        from portfolios.models import Site
        Site.objects.create(
            user=instance,
            title=f"{instance.username}'s Portfolio"
        )
