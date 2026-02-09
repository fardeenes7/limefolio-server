# Migration Commands Quick Reference

This document provides quick reference for common migration commands for the Limefolio server.

## Basic Migration Commands

### Create migrations for all apps

```bash
python manage.py makemigrations
```

### Create migrations for a specific app

```bash
python manage.py makemigrations <app_name>
# Examples:
python manage.py makemigrations portfolios
python manage.py makemigrations projects
python manage.py makemigrations experiences
python manage.py makemigrations blog
python manage.py makemigrations core
python manage.py makemigrations media
```

### Apply all migrations

```bash
python manage.py migrate
```

### Apply migrations for a specific app

```bash
python manage.py migrate <app_name>
# Example:
python manage.py migrate portfolios
```

### Show migration status

```bash
python manage.py showmigrations
```

### Show migration status for a specific app

```bash
python manage.py showmigrations <app_name>
```

## Advanced Migration Commands

### Show SQL for a migration

```bash
python manage.py sqlmigrate <app_name> <migration_number>
# Example:
python manage.py sqlmigrate portfolios 0001
```

### Rollback to a specific migration

```bash
python manage.py migrate <app_name> <migration_number>
# Example (rollback to migration 0001):
python manage.py migrate portfolios 0001
# Example (rollback all migrations for an app):
python manage.py migrate portfolios zero
```

### Create an empty migration (for data migrations)

```bash
python manage.py makemigrations --empty <app_name>
```

### Merge conflicting migrations

```bash
python manage.py makemigrations --merge
```

## Vercel Deployment Migration Commands

### Automatic migrations (during build)

Migrations run automatically during Vercel deployment via `build.sh`:

```bash
python manage.py migrate --noinput
```

### Manual migration after deployment

If you need to run migrations manually after deployment:

1. **Pull production environment variables:**

    ```bash
    vercel env pull .env.production
    ```

2. **Run migrations locally against production database:**

    ```bash
    export $(cat .env.production | xargs)
    python manage.py migrate
    ```

    Or on Windows:

    ```bash
    set -a
    source .env.production
    set +a
    python manage.py migrate
    ```

### Check deployment readiness

```bash
python manage.py check_deployment
```

This custom command checks:

- Database connectivity
- Pending migrations
- Environment variables
- CORS settings
- S3/R2 configuration
- Static files setup

## Database Reset (Development Only - DESTRUCTIVE!)

⚠️ **WARNING: These commands will delete all data!**

### Reset all migrations (SQLite - Development)

```bash
# Delete the database
rm db.sqlite3

# Delete all migration files (except __init__.py)
find . -path "*/migrations/*.py" -not -name "__init__.py" -not -path "*/venv/*" -delete
find . -path "*/migrations/*.pyc" -not -path "*/venv/*" -delete

# Recreate migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Reset PostgreSQL database (Production - DANGEROUS!)

```bash
# Connect to PostgreSQL
psql $DATABASE_URL

# Drop all tables
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO <your_db_user>;
GRANT ALL ON SCHEMA public TO public;

# Exit psql
\q

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

## Common Migration Issues & Solutions

### Issue: "No migrations to apply"

**Solution:** Run `python manage.py makemigrations` first.

### Issue: "Conflicting migrations detected"

**Solution:** Run `python manage.py makemigrations --merge`

### Issue: "Migration is being applied before its dependency"

**Solution:** Check the `dependencies` in your migration files and ensure they're correct.

### Issue: "Table already exists"

**Solution:**

1. Check if migrations are out of sync: `python manage.py showmigrations`
2. Fake the migration: `python manage.py migrate --fake <app_name> <migration_number>`

### Issue: "Column does not exist" after deployment

**Solution:** Ensure migrations ran successfully during build. Check Vercel logs.

## Pre-Deployment Checklist

Before deploying to Vercel, ensure:

- [ ] All local migrations are created: `python manage.py makemigrations`
- [ ] All migrations are committed to Git
- [ ] Migrations work locally: `python manage.py migrate`
- [ ] No migration conflicts: `python manage.py showmigrations`
- [ ] Database URL is set in Vercel environment variables
- [ ] `build.sh` has execute permissions: `chmod +x build.sh`
- [ ] Deployment check passes: `python manage.py check_deployment`

## Monitoring Migrations in Production

### View Vercel build logs

```bash
vercel logs --follow
```

### Check which migrations are applied in production

```bash
# Pull production environment
vercel env pull .env.production

# Check migration status
export $(cat .env.production | xargs)
python manage.py showmigrations
```

## Apps in Limefolio

The following apps have migrations:

- `core` - Core functionality, authentication, middleware
- `portfolios` - Portfolio/Site models
- `projects` - Project models
- `experiences` - Experience and Skills models
- `blog` - Blog posts and categories
- `media` - Media file management

## Useful Django Commands

### Create superuser

```bash
python manage.py createsuperuser
```

### Open Django shell

```bash
python manage.py shell
```

### Check for issues

```bash
python manage.py check
```

### Collect static files

```bash
python manage.py collectstatic --noinput
```

### Run development server

```bash
python manage.py runserver
```

## Resources

- [Django Migrations Documentation](https://docs.djangoproject.com/en/5.0/topics/migrations/)
- [Vercel Python Documentation](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/)
