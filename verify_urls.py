#!/usr/bin/env python
"""
Verify that all Experience and Skills API endpoints are properly registered.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'limefolio.settings')
django.setup()

from django.urls import get_resolver
from django.urls.resolvers import URLPattern, URLResolver

def list_urls(urlpatterns, prefix=''):
    """Recursively list all URL patterns"""
    urls = []
    for pattern in urlpatterns:
        if isinstance(pattern, URLResolver):
            urls.extend(list_urls(pattern.url_patterns, prefix + str(pattern.pattern)))
        elif isinstance(pattern, URLPattern):
            urls.append(prefix + str(pattern.pattern))
    return urls

def main():
    print("=" * 80)
    print("Experience and Skills API Endpoints Verification")
    print("=" * 80)
    
    resolver = get_resolver()
    all_urls = list_urls(resolver.url_patterns)
    
    # Filter for experience, skill, and social-link endpoints
    keywords = ['experience', 'skill', 'social']
    
    print("\n📋 Dashboard API Endpoints (Authenticated)")
    print("-" * 80)
    dashboard_urls = [url for url in all_urls if 'api/dashboard/' in url and any(k in url for k in keywords)]
    for url in sorted(set(dashboard_urls)):
        print(f"  /{url}")
    
    print("\n🌐 Public API Endpoints (Domain-based)")
    print("-" * 80)
    public_urls = [url for url in all_urls if 'api/public/' in url and any(k in url for k in keywords)]
    for url in sorted(set(public_urls)):
        print(f"  /{url}")
    
    print("\n🔑 External API Endpoints (API Key)")
    print("-" * 80)
    external_urls = [url for url in all_urls if 'v1/' in url and any(k in url for k in keywords)]
    for url in sorted(set(external_urls)):
        print(f"  /{url}")
    
    print("\n" + "=" * 80)
    print(f"✅ Total endpoints found: {len(dashboard_urls) + len(public_urls) + len(external_urls)}")
    print("=" * 80)
    
    # Verify expected endpoints exist
    expected = [
        'experiences/',
        'skills/',
        'social-links/',
    ]
    
    print("\n🔍 Verification:")
    all_found = True
    
    # Check Dashboard API
    print("\n  Dashboard API:")
    for endpoint in expected:
        found = any(f'api/dashboard/^{endpoint}' in url for url in all_urls)
        status = "✅" if found else "❌"
        print(f"    {status} /api/dashboard/{endpoint}")
        if not found:
            all_found = False
    
    # Check Public API
    print("\n  Public API:")
    for endpoint in expected:
        found = any(f'api/public/^{endpoint}' in url for url in all_urls)
        status = "✅" if found else "❌"
        print(f"    {status} /api/public/{endpoint}")
        if not found:
            all_found = False
    
    # Check External API
    print("\n  External API:")
    for endpoint in expected:
        found = any(f'v1/^{endpoint}' in url for url in all_urls)
        status = "✅" if found else "❌"
        print(f"    {status} /v1/{endpoint}")
        if not found:
            all_found = False
    
    if all_found:
        print("\n🎉 All expected endpoints are registered!")
    else:
        print("\n⚠️  Some endpoints are missing!")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
