# Vercel Deployment Guide for Limefolio Server

This guide will help you deploy the Limefolio Django backend to Vercel.

## Prerequisites

1. A Vercel account (sign up at https://vercel.com)
2. Vercel CLI installed: `npm i -g vercel`
3. A PostgreSQL database (recommended providers: Neon, Supabase, Railway, or Vercel Postgres)
4. AWS S3 or Cloudflare R2 bucket for media storage

## Environment Variables

Before deploying, you need to set up the following environment variables in your Vercel project settings:

### Required Variables

```bash
# Django Core
SECRET_KEY=your-production-secret-key-here
DEBUG=False
ALLOWED_HOSTS=.vercel.app,yourdomain.com

# Database (PostgreSQL required for production)
DATABASE_URL=postgresql://user:password@host:port/database

# CORS Settings
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# AWS S3 / Cloudflare R2 (Required for media storage)
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_ENDPOINT_URL=https://your-endpoint-url
AWS_S3_CUSTOM_DOMAIN=your-custom-domain
AWS_S3_REGION_NAME=auto
AWS_QUERYSTRING_AUTH=False

# OAuth (Optional - for social login)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# Email (Optional)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Frontend URL
FRONTEND_URL=https://yourdomain.com
```

## Deployment Steps

### Option 1: Deploy via Vercel CLI

1. **Login to Vercel**

    ```bash
    vercel login
    ```

2. **Navigate to the server directory**

    ```bash
    cd /home/fardeen/Projects/limefolio/server
    ```

3. **Deploy to production**

    ```bash
    vercel --prod
    ```

4. **Set environment variables** (if not already set)
    ```bash
    vercel env add SECRET_KEY
    vercel env add DATABASE_URL
    # ... add all other required variables
    ```

### Option 2: Deploy via Vercel Dashboard

1. Go to https://vercel.com/new
2. Import your Git repository
3. Set the root directory to `server`
4. Add all environment variables in the project settings
5. Deploy

## Database Setup

### Using Neon (Recommended)

1. Sign up at https://neon.tech
2. Create a new project
3. Copy the connection string
4. Add it as `DATABASE_URL` in Vercel environment variables

### Using Supabase

1. Sign up at https://supabase.com
2. Create a new project
3. Go to Settings > Database
4. Copy the connection string (use "Connection pooling" for better performance)
5. Add it as `DATABASE_URL` in Vercel environment variables

### Using Vercel Postgres

1. Go to your Vercel project dashboard
2. Navigate to Storage tab
3. Create a new Postgres database
4. The `DATABASE_URL` will be automatically added to your environment variables

## Storage Setup (S3/R2)

### Using Cloudflare R2 (Recommended - Free tier available)

1. Sign up at https://cloudflare.com
2. Go to R2 Object Storage
3. Create a new bucket
4. Create an API token with read/write permissions
5. Set up a custom domain for the bucket (optional but recommended)
6. Add the credentials to Vercel environment variables:
    - `AWS_ACCESS_KEY_ID`: Your R2 access key
    - `AWS_SECRET_ACCESS_KEY`: Your R2 secret key
    - `AWS_STORAGE_BUCKET_NAME`: Your bucket name
    - `AWS_S3_ENDPOINT_URL`: Your R2 endpoint (e.g., https://[account-id].r2.cloudflarestorage.com)
    - `AWS_S3_CUSTOM_DOMAIN`: Your custom domain or R2 public URL

### Using AWS S3

1. Create an S3 bucket
2. Create an IAM user with S3 permissions
3. Add the credentials to Vercel environment variables

## Post-Deployment

### Running Migrations Manually (if needed)

The `build.sh` script automatically runs migrations during deployment. However, if you need to run migrations manually:

```bash
# Using Vercel CLI
vercel env pull .env.production
python manage.py migrate --settings=limefolio.settings
```

### Creating a Superuser

After deployment, you may want to create a superuser:

```bash
# Connect to your production database locally
python manage.py createsuperuser --settings=limefolio.settings
```

Or use Django shell:

```bash
python manage.py shell --settings=limefolio.settings
```

Then:

```python
from django.contrib.auth import get_user_model
User = get_user_model()
User.objects.create_superuser('admin', 'admin@example.com', 'your-secure-password')
```

## Monitoring and Logs

- View deployment logs in Vercel Dashboard
- Check function logs in the Vercel project > Functions tab
- Monitor database performance in your database provider's dashboard

## Troubleshooting

### Issue: Migrations not running

**Solution**: Check the build logs in Vercel dashboard. Ensure `DATABASE_URL` is set correctly.

### Issue: Static files not loading

**Solution**: Ensure `collectstatic` runs successfully in `build.sh`. Check the build logs.

### Issue: Media uploads failing

**Solution**: Verify S3/R2 credentials are correct and the bucket has proper CORS settings.

### Issue: CORS errors

**Solution**: Update `CORS_ALLOWED_ORIGINS` to include your frontend domain.

### Issue: Database connection errors

**Solution**:

- Verify `DATABASE_URL` format: `postgresql://user:password@host:port/database`
- Ensure your database allows connections from Vercel's IP addresses
- For Neon/Supabase, use connection pooling URLs

## Custom Domain

1. Go to your Vercel project settings
2. Navigate to Domains
3. Add your custom domain
4. Update DNS records as instructed
5. Update `ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS` environment variables

## Security Checklist

- [ ] `DEBUG=False` in production
- [ ] Strong `SECRET_KEY` set
- [ ] `ALLOWED_HOSTS` configured correctly
- [ ] Database credentials secured
- [ ] S3/R2 bucket has proper permissions
- [ ] CORS origins limited to your frontend domains
- [ ] HTTPS enabled (automatic with Vercel)
- [ ] Environment variables set in Vercel (not in code)

## Useful Commands

```bash
# View deployment logs
vercel logs

# Pull environment variables
vercel env pull

# Redeploy
vercel --prod

# View project info
vercel inspect
```

## Additional Resources

- [Vercel Python Documentation](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/)
- [Vercel Environment Variables](https://vercel.com/docs/concepts/projects/environment-variables)
