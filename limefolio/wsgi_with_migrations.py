"""
WSGI config for limefolio project with automatic migrations on Vercel.

This version runs migrations automatically on cold starts when deployed to Vercel.
Use this if the package.json build approach doesn't work.

To use this file:
1. Backup current wsgi.py: cp limefolio/wsgi.py limefolio/wsgi.py.backup
2. Replace wsgi.py with this file: cp limefolio/wsgi_with_migrations.py limefolio/wsgi.py
3. Deploy to Vercel

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'limefolio.settings')

# Run migrations on cold start when deployed to Vercel
# This ensures migrations are always applied before the app starts
if os.environ.get('VERCEL') or os.environ.get('VERCEL_ENV'):
    import django
    django.setup()
    from django.core.management import call_command
    
    print("🚀 Vercel deployment detected - Running migrations...")
    try:
        # Run migrations
        call_command('migrate', '--noinput', verbosity=1)
        print("✓ Migrations applied successfully")
        
        # Optionally create superuser (only if it doesn't exist)
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            if not User.objects.filter(username='fardeen.es7').exists():
                User.objects.create_superuser(
                    'fardeen.es7',
                    'fardeen.es7@gmail.com',
                    'changeme'
                )
                print("✓ Superuser created")
        except Exception as e:
            print(f"⚠ Superuser creation skipped: {e}")
            
    except Exception as e:
        print(f"⚠ Migration error: {e}")
        # Don't fail the deployment if migrations fail
        # This allows the app to start even if migrations have issues

application = get_wsgi_application()
app = application
