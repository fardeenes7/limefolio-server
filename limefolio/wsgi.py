"""
WSGI config for limefolio project.

It exposes the WSGI callable as a module-level variable named ``app``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'limefolio.settings')

# Run migrations on cold start when deployed to Vercel
# This is the most reliable way to ensure migrations run on Vercel serverless
if os.environ.get('VERCEL') or os.environ.get('VERCEL_ENV'):
    import django
    django.setup()
    from django.core.management import call_command
    
    print("🚀 Vercel deployment detected - Running migrations...")
    try:
        # Run migrations
        call_command('migrate', '--noinput', verbosity=0)
        print("✓ Migrations applied successfully")
        
        # Create superuser if it doesn't exist
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            if not User.objects.filter(username='fardeen.es7').exists():
                User.objects.create_superuser(
                    'fardeen.es7',
                    'fardeen.es7@gmail.com',
                    'changeme'
                )
                print("✓ Superuser created: fardeen.es7")
            else:
                print("✓ Superuser already exists")
        except Exception as e:
            print(f"⚠ Superuser creation skipped: {e}")
            
    except Exception as e:
        print(f"⚠ Migration error: {e}")
        # Don't fail the deployment if migrations fail

application = get_wsgi_application()
app = application
