"""
Vercel Build Hook for Django
This runs on every cold start to ensure migrations and static files are ready.
Place this file in your Django project root (same directory as manage.py).
"""

import os

def run_build_tasks():
    """Run Django migrations and collect static files on cold start."""
    print("=" * 60)
    print("Running Django build tasks on cold start...")
    print("=" * 60)
    
    # Set up Django environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'limefolio.settings')
    
    try:
        import django
        django.setup()
        
        from django.core.management import call_command
        
        # Run migrations
        print("\n[1/3] Running database migrations...")
        try:
            call_command('migrate', '--noinput', verbosity=1)
            print("✓ Migrations completed successfully")
        except Exception as e:
            print(f"⚠ Migration warning: {e}")
        
        # Collect static files
        print("\n[2/3] Collecting static files...")
        try:
            call_command('collectstatic', '--noinput', '--clear', verbosity=1)
            print("✓ Static files collected successfully")
        except Exception as e:
            print(f"⚠ Static files warning: {e}")
        
        # Create superuser if needed (optional)
        if os.environ.get('CREATE_SUPERUSER', 'false').lower() == 'true':
            print("\n[3/3] Creating superuser (if not exists)...")
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                username = os.environ.get('SUPERUSER_USERNAME', 'fardeen.es7')
                email = os.environ.get('SUPERUSER_EMAIL', 'fardeen.es7@gmail.com')
                password = os.environ.get('SUPERUSER_PASSWORD', 'changeme')
                
                if not User.objects.filter(username=username).exists():
                    User.objects.create_superuser(username, email, password, first_name='Fardeen', last_name='Ehsan')
                    print(f"✓ Superuser '{username}' created")
                else:
                    print(f"✓ Superuser '{username}' already exists")
            except Exception as e:
                print(f"⚠ Superuser creation warning: {e}")
        
        print("\n" + "=" * 60)
        print("Build tasks completed!")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"Error during build tasks: {e}")
        # Don't raise - let the app start anyway

# Run on import (cold start)
if __name__ != '__main__':
    run_build_tasks()
