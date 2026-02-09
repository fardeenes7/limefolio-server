#!/bin/bash

# Vercel Build Script for Django
# Runs via package.json "vercel-build" script after Python dependencies are installed

echo "Starting Django build tasks..."

# Verify Django is available
if ! python3 -c "import django" 2>/dev/null; then
    echo "Error: Django not available. Skipping build tasks."
    echo "Migrations will run via WSGI on cold start."
    exit 0
fi

echo "Django found, proceeding with build tasks..."

# Collect static files
echo "Collecting static files..."
python3 manage.py collectstatic --noinput --clear || echo "Warning: collectstatic failed"

# Run database migrations (if DATABASE_URL is available)
if [ -n "$DATABASE_URL" ]; then
    echo "Running database migrations..."
    python3 manage.py migrate --noinput || echo "Warning: migrations failed, will retry on cold start"
    
    # Create superuser if needed
    echo "Creating superuser (if not exists)..."
    python3 manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='fardeen.es7').exists() or User.objects.create_superuser('fardeen.es7', 'fardeen.es7@gmail.com', 'changeme')" || echo "Warning: superuser creation failed, will retry on cold start"
else
    echo "DATABASE_URL not set, skipping migrations (will run on cold start)"
fi

echo "Build tasks completed!"



