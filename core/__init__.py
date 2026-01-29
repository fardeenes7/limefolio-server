"""
Core app initialization.
Import schema extensions to register them with drf-spectacular.
"""
from core.schema import (
    SocialAuthenticationScheme,
    APIKeyAuthenticationScheme,
    DomainBasedAuthenticationScheme
)

default_app_config = 'core.apps.CoreConfig'

__all__ = [
    'SocialAuthenticationScheme',
    'APIKeyAuthenticationScheme',
    'DomainBasedAuthenticationScheme',
]

