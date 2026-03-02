from django.db.models.signals import post_save
from django.dispatch import receiver
from media.models import Media
from portfolios.models import Site
from projects.models import Project

@receiver(post_save, sender=Media)
def revalidate_media_cache(sender, instance, **kwargs):
    """Trigger revalidation when media is updated/attached."""
    from core.revalidation import revalidate_public_cache
    
    # Try to find the associated site
    site = None
    if isinstance(instance.content_object, Site):
        site = instance.content_object
    elif isinstance(instance.content_object, Project):
        site = instance.content_object.site
    
    if site:
        # Revalidate the main site data tag
        revalidate_public_cache(tag=f"{site.subdomain}-site")
        
        # If it's a project image, revalidate the project specifically
        if isinstance(instance.content_object, Project):
            revalidate_public_cache(tag=f"{site.subdomain}-projects")
            revalidate_public_cache(tag=f"{site.subdomain}-project-{instance.content_object.slug}")
