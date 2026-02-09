"""
Management command to check deployment readiness and database connectivity.
Usage: python manage.py check_deployment
"""

from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings
import sys


class Command(BaseCommand):
    help = 'Check deployment readiness and database connectivity'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('Limefolio Deployment Check'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        # Check DEBUG mode
        self.stdout.write('\n1. Checking DEBUG mode...')
        if settings.DEBUG:
            self.stdout.write(self.style.WARNING('   ⚠ DEBUG is True (should be False in production)'))
        else:
            self.stdout.write(self.style.SUCCESS('   ✓ DEBUG is False'))
        
        # Check SECRET_KEY
        self.stdout.write('\n2. Checking SECRET_KEY...')
        if settings.SECRET_KEY == 'django-insecure-=cldztbc4jg&xl0!x673!*v2_=p$$eu)=7*f#d0#zs$44xx-h^':
            self.stdout.write(self.style.ERROR('   ✗ Using default SECRET_KEY (SECURITY RISK!)'))
        else:
            self.stdout.write(self.style.SUCCESS('   ✓ SECRET_KEY is set'))
        
        # Check ALLOWED_HOSTS
        self.stdout.write('\n3. Checking ALLOWED_HOSTS...')
        if settings.ALLOWED_HOSTS:
            self.stdout.write(self.style.SUCCESS(f'   ✓ ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}'))
        else:
            self.stdout.write(self.style.ERROR('   ✗ ALLOWED_HOSTS is empty'))
        
        # Check database connectivity
        self.stdout.write('\n4. Checking database connectivity...')
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                db_name = settings.DATABASES['default']['ENGINE']
                self.stdout.write(self.style.SUCCESS(f'   ✓ Database connected ({db_name})'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ✗ Database connection failed: {str(e)}'))
            sys.exit(1)
        
        # Check migrations
        self.stdout.write('\n5. Checking migrations...')
        try:
            from django.db.migrations.executor import MigrationExecutor
            executor = MigrationExecutor(connection)
            plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
            
            if plan:
                self.stdout.write(self.style.WARNING(f'   ⚠ {len(plan)} unapplied migrations found'))
                for migration, backwards in plan:
                    self.stdout.write(f'     - {migration}')
            else:
                self.stdout.write(self.style.SUCCESS('   ✓ All migrations applied'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ✗ Migration check failed: {str(e)}'))
        
        # Check CORS settings
        self.stdout.write('\n6. Checking CORS settings...')
        if hasattr(settings, 'CORS_ALLOWED_ORIGINS') and settings.CORS_ALLOWED_ORIGINS:
            self.stdout.write(self.style.SUCCESS(f'   ✓ CORS_ALLOWED_ORIGINS: {settings.CORS_ALLOWED_ORIGINS}'))
        else:
            self.stdout.write(self.style.WARNING('   ⚠ CORS_ALLOWED_ORIGINS not set'))
        
        # Check S3/R2 configuration
        self.stdout.write('\n7. Checking media storage (S3/R2)...')
        try:
            storage_backend = settings.STORAGES['default']['BACKEND']
            if 'S3Storage' in storage_backend:
                bucket = settings.STORAGES['default']['OPTIONS'].get('bucket_name')
                endpoint = settings.STORAGES['default']['OPTIONS'].get('endpoint_url')
                self.stdout.write(self.style.SUCCESS('   ✓ S3/R2 configured'))
                self.stdout.write(f'     Bucket: {bucket}')
                self.stdout.write(f'     Endpoint: {endpoint}')
            else:
                self.stdout.write(self.style.WARNING(f'   ⚠ Using local storage: {storage_backend}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ✗ Storage check failed: {str(e)}'))
        
        # Check static files
        self.stdout.write('\n8. Checking static files...')
        if hasattr(settings, 'STATIC_ROOT') and settings.STATIC_ROOT:
            self.stdout.write(self.style.SUCCESS(f'   ✓ STATIC_ROOT: {settings.STATIC_ROOT}'))
        else:
            self.stdout.write(self.style.WARNING('   ⚠ STATIC_ROOT not set'))
        
        # Summary
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('Deployment check completed!'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write('\nNext steps:')
        self.stdout.write('  1. Fix any errors or warnings above')
        self.stdout.write('  2. Run: python manage.py migrate')
        self.stdout.write('  3. Run: python manage.py collectstatic')
        self.stdout.write('  4. Deploy to Vercel: vercel --prod')
        self.stdout.write('')
