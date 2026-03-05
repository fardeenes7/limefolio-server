from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_site(sender, instance, created, **kwargs):
    """Auto-create Site when a new user is created via OAuth."""
    if created:
        from portfolios.models import Site
        Site.objects.create(
            user=instance,
            title=f"{instance.username}'s Portfolio"
        )

@receiver(post_save, sender='portfolios.Site')
def revalidate_site_cache(sender, instance, **kwargs):
    """Trigger revalidation when Site settings are updated."""
    from core.revalidation import revalidate_site_tags
    revalidate_site_tags(instance, "site")

def revalidate_site_related(instance):
    """Helper to revalidate site cache when a related model is saved."""
    from core.revalidation import revalidate_site_tags
    revalidate_site_tags(instance.site, "site")

@receiver(post_save, sender='projects.Project')
def revalidate_project_cache(sender, instance, **kwargs):
    """Trigger revalidation when a Project is updated."""
    from core.revalidation import revalidate_site_tags
    
    # Revalidate site-wide project list and specific project page
    revalidate_site_tags(instance.site, "projects", f"project-{instance.slug}")
    
    # Revalidate the main site data (it might contain project counts/summaries)
    revalidate_site_related(instance)

@receiver(post_save, sender='experiences.Experience')
@receiver(post_save, sender='experiences.Skill')
@receiver(post_save, sender='experiences.SocialLink')
def revalidate_experience_related_cache(sender, instance, **kwargs):
    """Trigger revalidation when experiences/skills/social links are updated."""
    revalidate_site_related(instance)
