from django.http import JsonResponse
from django.core.management import call_command
from django.views import View

class RunMigrationsView(View):
    """Public endpoint to trigger database migrations.
    This view runs ``manage.py migrate`` without input and returns a JSON
    response indicating success or failure. It is deliberately lightweight
    and does not require authentication – use with caution in production.
    """

    def get(self, request, *args, **kwargs):
        try:
            # Run migrations silently
            call_command('migrate', '--noinput', verbosity=0)
            return JsonResponse({"status": "ok", "message": "Migrations applied"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
