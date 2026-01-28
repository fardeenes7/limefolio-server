"""
Portfolio app configuration
"""
from django.apps import AppConfig


class PortfolioConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'portfolio'
    
    def ready(self):
        import portfolio.signals  # noqa
    verbose_name = 'Portfolio Sites'
