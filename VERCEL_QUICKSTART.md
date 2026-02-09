# 🚀 Vercel Deployment - Quick Start

This guide will get your Limefolio server deployed to Vercel in minutes.

## 📋 Prerequisites

- [ ] Vercel account ([sign up here](https://vercel.com))
- [ ] PostgreSQL database (see [Database Setup](#database-setup))
- [ ] S3/R2 bucket for media storage (see [Storage Setup](#storage-setup))
- [ ] Vercel CLI: `npm i -g vercel`

## 🎯 Quick Deploy (5 minutes)

### 1. Set up Database

**Option A: Neon (Recommended - Free tier)**

```bash
# 1. Go to https://neon.tech
# 2. Create a new project
# 3. Copy the connection string
```

**Option B: Vercel Postgres**

```bash
# 1. Go to your Vercel dashboard
# 2. Create a new Postgres database
# 3. Connection string will be auto-added to your project
```

### 2. Set up Storage (S3/R2)

**Cloudflare R2 (Recommended - Free tier)**

```bash
# 1. Go to https://cloudflare.com
# 2. Navigate to R2 Object Storage
# 3. Create a new bucket
# 4. Create an API token
# 5. Note down:
#    - Access Key ID
#    - Secret Access Key
#    - Bucket Name
#    - Endpoint URL
```

### 3. Deploy to Vercel

```bash
# Navigate to server directory
cd /home/fardeen/Projects/limefolio/server

# Login to Vercel
vercel login

# Deploy
vercel --prod
```

### 4. Set Environment Variables

After deployment, set these in Vercel Dashboard (Project Settings → Environment Variables):

**Required:**

```bash
SECRET_KEY=<generate-with-command-below>
DEBUG=False
ALLOWED_HOSTS=.vercel.app,yourdomain.com
DATABASE_URL=postgresql://user:password@host:port/database
CORS_ALLOWED_ORIGINS=https://yourdomain.com

# S3/R2
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_ENDPOINT_URL=https://your-endpoint
AWS_S3_CUSTOM_DOMAIN=your-domain
AWS_S3_REGION_NAME=auto
AWS_QUERYSTRING_AUTH=False
```

**Generate SECRET_KEY:**

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### 5. Redeploy

After setting environment variables:

```bash
vercel --prod
```

## ✅ Verify Deployment

Check your deployment:

```bash
# View logs
vercel logs

# Test the API
curl https://your-project.vercel.app/api/

# Check admin panel
open https://your-project.vercel.app/admin/
```

## 🔧 Local Testing

Before deploying, test locally:

```bash
# Run deployment check
python manage.py check_deployment

# Run test script
./test_deployment.sh

# Test migrations
python manage.py migrate --dry-run
```

## 📚 Detailed Documentation

- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Complete deployment guide
- **[MIGRATIONS.md](./MIGRATIONS.md)** - Migration commands reference
- **[.env.example](./.env.example)** - Environment variables template

## 🐛 Troubleshooting

### Migrations not running?

```bash
# Check build logs in Vercel dashboard
vercel logs

# Manually run migrations
vercel env pull .env.production
export $(cat .env.production | xargs)
python manage.py migrate
```

### Static files not loading?

```bash
# Ensure STATIC_ROOT is set in settings.py
# Check build logs for collectstatic output
```

### Database connection errors?

```bash
# Verify DATABASE_URL format
# Ensure database allows Vercel IP addresses
# Use connection pooling for Neon/Supabase
```

## 🔐 Security Checklist

- [ ] `DEBUG=False` in production
- [ ] Strong `SECRET_KEY` generated
- [ ] `ALLOWED_HOSTS` configured
- [ ] Database credentials secured
- [ ] S3/R2 bucket permissions set correctly
- [ ] CORS origins limited to your domains
- [ ] Environment variables set in Vercel (not in code)

## 📞 Support

- [Vercel Documentation](https://vercel.com/docs)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/)
- [Limefolio Issues](https://github.com/fardeenes7/limefolio/issues)

---

**Ready to deploy?** Run `vercel --prod` 🚀
