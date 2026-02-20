import os
from django.core.wsgi import get_wsgi_application

# Standard WSGI application for Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'limefolio.settings')
application = get_wsgi_application()
app = application