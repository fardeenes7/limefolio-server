import os
from django.core.wsgi import get_wsgi_application
import django
from django.core.management import call_command

django.setup()


# Run migrations on cold start when deployed to Vercel

print("🚀 Vercel deployment detected - Running migrations...")
try:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'limefolio.settings')
    # Run migrations
    call_command('migrate', '--noinput', verbosity=0)
    print("✓ Migrations applied successfully")
        
except Exception as e:
    print(f"⚠ Migration error: {e}")
    # Don't fail the deployment if migrations fail

application = get_wsgi_application()
app = application