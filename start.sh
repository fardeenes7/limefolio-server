#!/bin/bash
# Exit on error
set -e

echo "Running migrations..."
python manage.py migrate --noinput

if [ "$DEBUG" = "True" ] || [ "$DEBUG" = "true" ] || [ "$DEBUG" = "1" ]; then
    echo "Starting Development Server with Hot Reload..."
    exec python manage.py runserver 0.0.0.0:8000
else
    echo "Collecting static files..."
    python manage.py collectstatic --noinput

    echo "Starting Gunicorn..."
    exec gunicorn limefolio.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120
fi
