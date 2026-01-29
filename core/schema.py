"""
OpenAPI schema extensions for custom authentication classes.
"""
from drf_spectacular.extensions import OpenApiAuthenticationExtension


class SocialAuthenticationScheme(OpenApiAuthenticationExtension):
    """OAuth2 Social Authentication extension for drf-spectacular"""
    target_class = 'drf_social_oauth2.authentication.SocialAuthentication'
    name = 'OAuth2'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'oauth2',
            'flows': {
                'authorizationCode': {
                    'authorizationUrl': '/api/auth/authorize/',
                    'tokenUrl': '/api/auth/token/',
                    'scopes': {
                        'read': 'Read access',
                        'write': 'Write access',
                    }
                }
            }
        }


class APIKeyAuthenticationScheme(OpenApiAuthenticationExtension):
    """API Key Authentication extension for drf-spectacular"""
    target_class = 'core.auth.authentication.APIKeyAuthentication'
    name = 'ApiKeyAuth'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'apiKey',
            'in': 'header',
            'name': 'X-API-Key',
            'description': 'API Key authentication for external API access'
        }


class DomainBasedAuthenticationScheme(OpenApiAuthenticationExtension):
    """Domain-based Authentication extension for drf-spectacular"""
    target_class = 'core.auth.authentication.DomainBasedAuthentication'
    name = 'DomainAuth'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Host',
            'description': 'Domain-based authentication for site-specific access'
        }
