#!/bin/bash

# Quick deployment test script
# This script simulates the Vercel build process locally

echo "=========================================="
echo "Limefolio Deployment Test"
echo "=========================================="
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found"
    echo "   Creating from .env.example..."
    cp .env.example .env
    echo "   Please update .env with your actual values"
    echo ""
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Run deployment check
echo "1. Running deployment check..."
python3 manage.py check_deployment
echo ""

# Check for pending migrations
echo "2. Checking for pending migrations..."
python3 manage.py showmigrations | grep "\[ \]" && echo "   ⚠️  Pending migrations found" || echo "   ✓ No pending migrations"
echo ""

# Test database connection
echo "3. Testing database connection..."
python3 manage.py check --database default && echo "   ✓ Database check passed" || echo "   ✗ Database check failed"
echo ""

# Test static files collection
echo "4. Testing static files collection..."
python3 manage.py collectstatic --noinput --dry-run > /dev/null 2>&1 && echo "   ✓ Static files check passed" || echo "   ✗ Static files check failed"
echo ""

# Run Django system checks
echo "5. Running Django system checks..."
python3 manage.py check && echo "   ✓ System checks passed" || echo "   ✗ System checks failed"
echo ""

echo "=========================================="
echo "Deployment test completed!"
echo "=========================================="
echo ""
echo "If all checks passed, you're ready to deploy:"
echo "  vercel --prod"
echo ""
