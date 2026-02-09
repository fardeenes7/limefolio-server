# 🔧 Vercel Deployment Fix - Migration Support

## Problem

The `build.sh` script wasn't running because Vercel's `builds` configuration ignores the `buildCommand` property. This caused migrations not to run during deployment.

## Solution

I've implemented **three different approaches** - you can choose which one works best:

---

## ✅ **RECOMMENDED: Approach 1 - Using package.json**

This is the simplest and most reliable approach.

### Files Created:

- `.python-version` - Specifies Python 3.9
- `package.json` - Triggers build script via npm
- Updated `vercel.json` - Simplified configuration

### How it works:

Vercel detects `package.json` and runs the `build` script, which executes `build.sh` containing migrations.

### Current Configuration:

```json
// vercel.json
{
    "buildCommand": "bash build.sh",
    "routes": [...]
}

// package.json
{
  "scripts": {
    "build": "bash build.sh"
  }
}
```

### Deploy:

```bash
git add .
git commit -m "Fix: Add package.json for build script"
git push
```

Vercel will automatically:

1. Detect Python 3.9 from `.python-version`
2. Run `npm run build` (which runs `build.sh`)
3. Execute migrations
4. Deploy the app

---

## 🔄 **Approach 2 - Run Migrations in WSGI (Alternative)**

If Approach 1 doesn't work, you can run migrations on application startup.

### Update `limefolio/wsgi.py`:

```python
"""
WSGI config for api project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'limefolio.settings')

# Run migrations on cold start (Vercel serverless)
if os.environ.get('VERCEL'):
    import django
    django.setup()
    from django.core.management import call_command
    try:
        call_command('migrate', '--noinput')
        print("✓ Migrations applied successfully")
    except Exception as e:
        print(f"⚠ Migration error: {e}")

application = get_wsgi_application()
app = application
```

### Pros:

- Guaranteed to run on every cold start
- No build configuration needed

### Cons:

- Adds latency to first request
- Migrations run on every cold start (not just deploys)

---

## 🛠️ **Approach 3 - Manual Migrations (Fallback)**

If automated migrations don't work, run them manually after each deployment.

### Steps:

1. **Deploy your code:**

    ```bash
    git push
    ```

2. **Pull production environment:**

    ```bash
    vercel env pull .env.production
    ```

3. **Run migrations locally against production DB:**
    ```bash
    export $(cat .env.production | xargs)
    python3 manage.py migrate
    ```

### Or use Vercel CLI:

```bash
# Set up a one-time migration command
vercel env add MIGRATION_COMMAND
# Value: python manage.py migrate --noinput

# Then create a serverless function to run it
# (More complex, see Vercel docs)
```

---

## 🧪 Testing

### Test Approach 1 (package.json):

```bash
# Locally simulate Vercel build
npm run build

# Should output:
# Starting Vercel build process...
# Installing Python dependencies...
# Collecting static files...
# Running database migrations...
# Build process completed successfully!
```

### Test Approach 2 (WSGI):

```bash
# Set VERCEL env var
export VERCEL=1

# Run server
python3 manage.py runserver

# Check console for migration output
```

---

## 📋 Current Status

✅ `.python-version` created (Python 3.9)  
✅ `package.json` created with build script  
✅ `vercel.json` updated (simplified)  
✅ `build.sh` ready with migrations  
✅ `vercel_build.sh` created (alternative)

---

## 🚀 Recommended Next Steps

1. **Commit and push the changes:**

    ```bash
    git add .python-version package.json vercel.json
    git commit -m "Fix: Add package.json for Vercel build script"
    git push
    ```

2. **Monitor the deployment:**

    ```bash
    vercel logs --follow
    ```

3. **Look for in the logs:**

    ```
    Running "npm run build"
    > build
    > bash build.sh

    Starting Vercel build process...
    Running database migrations...
    ```

4. **If Approach 1 doesn't work:**
    - Try Approach 2 (WSGI migrations)
    - Or use Approach 3 (manual migrations)

---

## 🐛 Troubleshooting

### Build script still not running?

**Check Vercel build logs for:**

```
Running "npm run build"
```

If you don't see this, Vercel isn't detecting package.json.

**Solution:**

- Ensure `package.json` is in the root directory
- Ensure it's committed to git
- Try redeploying

### Python version still wrong?

**Check for:**

```
Using python version: 3.9
```

If it says 3.12:

- Ensure `.python-version` contains just `3.9`
- Ensure it's committed to git

### Migrations failing?

**Check:**

- `DATABASE_URL` is set in Vercel environment variables
- Database is accessible from Vercel
- No syntax errors in migration files

---

## 📞 Need Help?

If none of these approaches work:

1. Share the full Vercel build log
2. Check if `package.json` is being detected
3. Verify environment variables are set
4. Try the WSGI approach as a temporary solution

---

## 🎯 Summary

**Current setup uses Approach 1 (package.json)**

This should work for most cases. If it doesn't, you have two backup approaches ready to go.

The key files are:

- `.python-version` → Python 3.9
- `package.json` → Triggers build.sh
- `build.sh` → Runs migrations
- `vercel.json` → Simplified config

**Deploy and test!** 🚀
