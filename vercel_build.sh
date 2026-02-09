#!/bin/bash

# Vercel Build Script for Django
# This script runs during the Vercel build process
# Vercel automatically runs this if it exists

echo "Starting Vercel build process..."

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Create superuser if needed (optional - only for initial setup)
echo "Creating superuser (if not exists)..."
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='fardeen.es7').exists() or User.objects.create_superuser('fardeen.es7', 'fardeen.es7@gmail.com', 'changeme')"

echo "Build process completed successfully!"
