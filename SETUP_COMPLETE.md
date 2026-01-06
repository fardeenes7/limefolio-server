# Django REST Framework Setup - Complete ✅

## What Was Installed & Configured

### 1. **Packages Installed**

-   ✅ `djangorestframework` - REST API framework
-   ✅ `djangorestframework-simplejwt` - JWT authentication
-   ✅ `dj-rest-auth` - Authentication endpoints
-   ✅ `django-allauth` - Social authentication
-   ✅ `django-cors-headers` - CORS support
-   ✅ `python-decouple` - Environment variables
-   ✅ `psycopg2-binary` - PostgreSQL support
-   ✅ `dj-database-url` - Database URL parsing

### 2. **Environment Variables Setup**

-   ✅ Created `.env.example` template
-   ✅ Created `.env` file with default values
-   ✅ Configured all settings to use environment variables

### 3. **Authentication App Created**

Location: `/authentication/`

Files created:

-   ✅ `serializers.py` - User and registration serializers
-   ✅ `views.py` - Social login, token exchange, refresh, logout views
-   ✅ `urls.py` - API endpoint routing

### 4. **Settings Configuration**

Updated `api/settings.py` with:

-   ✅ Environment variable loading
-   ✅ REST Framework configuration
-   ✅ JWT settings (access & refresh tokens)
-   ✅ Social authentication (Google, GitHub)
-   ✅ CORS settings
-   ✅ Email configuration
-   ✅ Database configuration (SQLite default, PostgreSQL ready)

### 5. **Database Setup**

-   ✅ Migrations run successfully
-   ✅ Token blacklist enabled for JWT rotation
-   ✅ All authentication tables created

### 6. **API Endpoints Available**

**Base URL:** `http://localhost:8000/api/auth/`

#### Registration & Login

-   `POST /api/auth/registration/` - Register new user
-   `POST /api/auth/login/` - Login with email/password

#### Social Authentication

-   `POST /api/auth/social/google/` - Google OAuth login
-   `POST /api/auth/social/github/` - GitHub OAuth login
-   `POST /api/auth/social/token-exchange/` - Exchange social token for JWT

#### Token Management

-   `POST /api/auth/token/refresh/` - Refresh access token
-   `POST /api/auth/token/verify/` - Verify token validity

#### User Management

-   `GET /api/auth/user/` - Get current user profile
-   `POST /api/auth/logout/` - Logout (blacklist token)

### 7. **Documentation Created**

-   ✅ `AUTH_README.md` - Complete API documentation
-   ✅ `test_auth.py` - Python test script
-   ✅ `Limefolio_Auth_API.postman_collection.json` - Postman collection

## Next Steps

### 1. Configure Social OAuth Providers

#### Google OAuth:

1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Create OAuth 2.0 credentials
3. Add to `.env`:
    ```
    GOOGLE_CLIENT_ID=your-client-id
    GOOGLE_CLIENT_SECRET=your-client-secret
    ```

#### GitHub OAuth:

1. Visit [GitHub Developer Settings](https://github.com/settings/developers)
2. Create new OAuth App
3. Add to `.env`:
    ```
    GITHUB_CLIENT_ID=your-client-id
    GITHUB_CLIENT_SECRET=your-client-secret
    ```

### 2. Start the Development Server

```bash
source venv/bin/activate
python manage.py runserver
```

### 3. Test the API

**Option 1: Using Python Script**

```bash
python test_auth.py
```

**Option 2: Using Postman**

-   Import `Limefolio_Auth_API.postman_collection.json`
-   Test all endpoints

**Option 3: Using cURL**

```bash
# Register
curl -X POST http://localhost:8000/api/auth/registration/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password1":"Test123!","password2":"Test123!"}'

# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}'
```

### 4. Frontend Integration

See `AUTH_README.md` for complete frontend integration examples with:

-   Registration flow
-   Login flow
-   Social authentication
-   Token refresh
-   Protected routes

### 5. Production Deployment

Before deploying to production:

1. **Update `.env`:**

    ```
    DEBUG=False
    SECRET_KEY=generate-new-secure-key
    ALLOWED_HOSTS=yourdomain.com
    DATABASE_URL=postgresql://...
    ```

2. **Enable email verification:**
   In `settings.py`:

    ```python
    ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
    ```

3. **Configure email backend:**
   Update email settings in `.env` with real SMTP credentials

4. **Use HTTPS:**
   All production traffic should use HTTPS

5. **Set up PostgreSQL:**
   Uncomment PostgreSQL configuration in `settings.py`

## File Structure

```
server/
├── api/
│   ├── settings.py          # ✅ Updated with all configurations
│   ├── urls.py              # ✅ Added authentication routes
│   └── ...
├── authentication/          # ✅ New app
│   ├── serializers.py       # ✅ User serializers
│   ├── views.py             # ✅ Auth views
│   ├── urls.py              # ✅ Auth routes
│   └── ...
├── .env                     # ✅ Environment variables
├── .env.example             # ✅ Template
├── requirements.txt         # ✅ Updated with all packages
├── AUTH_README.md           # ✅ Complete documentation
├── test_auth.py             # ✅ Test script
└── Limefolio_Auth_API.postman_collection.json  # ✅ Postman collection
```

## Environment Variables Reference

| Variable                     | Purpose                      | Default                                       |
| ---------------------------- | ---------------------------- | --------------------------------------------- |
| `SECRET_KEY`                 | Django secret key            | Auto-generated                                |
| `DEBUG`                      | Debug mode                   | `True`                                        |
| `ALLOWED_HOSTS`              | Allowed hosts                | `127.0.0.1,localhost,.vercel.app`             |
| `DATABASE_URL`               | Database connection          | SQLite                                        |
| `CORS_ALLOWED_ORIGINS`       | Frontend URLs                | `http://localhost:3000,http://localhost:5173` |
| `JWT_ACCESS_TOKEN_LIFETIME`  | Access token lifetime (min)  | `60`                                          |
| `JWT_REFRESH_TOKEN_LIFETIME` | Refresh token lifetime (min) | `1440`                                        |
| `GOOGLE_CLIENT_ID`           | Google OAuth ID              | -                                             |
| `GOOGLE_CLIENT_SECRET`       | Google OAuth secret          | -                                             |
| `GITHUB_CLIENT_ID`           | GitHub OAuth ID              | -                                             |
| `GITHUB_CLIENT_SECRET`       | GitHub OAuth secret          | -                                             |
| `FRONTEND_URL`               | Frontend URL                 | `http://localhost:3000`                       |

## Features Implemented

✅ **User Registration** - Email-based registration with password validation  
✅ **User Login** - Email/password authentication  
✅ **JWT Tokens** - Access and refresh token system  
✅ **Token Refresh** - Automatic token rotation  
✅ **Token Blacklist** - Secure logout with token invalidation  
✅ **Social Login** - Google and GitHub OAuth integration  
✅ **Token Exchange** - Convert social tokens to JWT  
✅ **User Profile** - Get current user information  
✅ **CORS Support** - Frontend integration ready  
✅ **Environment Variables** - Secure configuration management  
✅ **PostgreSQL Ready** - Easy database migration

## Support

For detailed API documentation, see `AUTH_README.md`

For issues or questions, check the Django REST Framework and dj-rest-auth documentation.
