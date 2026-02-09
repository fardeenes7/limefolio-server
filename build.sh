#!/bin/bash

# Vercel Build Script for Django
# This script runs during the Vercel build process

echo "Starting Vercel build process..."

# Skip pip install - Vercel's Python builder already handles this from requirements.txt
echo "Skipping pip install (handled by Vercel Python builder)..."

# Collect static files
echo "Collecting static files..."
python3 manage.py collectstatic --noinput --clear || echo "Warning: collectstatic failed, continuing..."

# Run database migrations
echo "Running database migrations..."
python3 manage.py migrate --noinput || echo "Warning: migrations failed, will retry on cold start"

# Create superuser if needed (optional - only for initial setup)
echo "Creating superuser (if not exists)..."
python3 manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='fardeen.es7').exists() or User.objects.create_superuser('fardeen.es7', 'fardeen.es7@gmail.com', 'changeme')" || echo "Warning: superuser creation failed, will retry on cold start"

echo "Build process completed!"

