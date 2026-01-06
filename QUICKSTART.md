# Quick Start Guide 🚀

## Server is Ready!

Your Django REST Framework server with social authentication is fully configured and running!

## What's Available Right Now

### 🔐 Authentication Endpoints

All endpoints are live at: `http://localhost:8000/api/auth/`

### 📝 Test It Now

**1. Register a new user:**

```bash
curl -X POST http://localhost:8000/api/auth/registration/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password1": "SecurePass123!",
    "password2": "SecurePass123!",
    "first_name": "Test",
    "last_name": "User"
  }'
```

**2. Login:**

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
```

You'll get back:

```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
        "id": 1,
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User"
    }
}
```

**3. Get user profile (use the access token from login):**

```bash
curl http://localhost:8000/api/auth/user/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 🔧 Configuration Needed for Social Login

### Google OAuth

1. Go to: https://console.cloud.google.com/
2. Create OAuth credentials
3. Add to `.env`:
    ```
    GOOGLE_CLIENT_ID=your-google-client-id
    GOOGLE_CLIENT_SECRET=your-google-client-secret
    ```

### GitHub OAuth

1. Go to: https://github.com/settings/developers
2. Create OAuth App
3. Add to `.env`:
    ```
    GITHUB_CLIENT_ID=your-github-client-id
    GITHUB_CLIENT_SECRET=your-github-client-secret
    ```

## 📚 Documentation

-   **Complete API Docs:** `AUTH_README.md`
-   **Setup Summary:** `SETUP_COMPLETE.md`
-   **Postman Collection:** `Limefolio_Auth_API.postman_collection.json`
-   **Test Script:** `test_auth.py`

## 🎯 Next Steps

1. **Configure OAuth providers** (see above)
2. **Test with Postman** - Import the collection
3. **Integrate with frontend** - See AUTH_README.md for examples
4. **Set up PostgreSQL** (optional) - Uncomment in settings.py

## 🌐 Available Endpoints

| Method | Endpoint                           | Description           |
| ------ | ---------------------------------- | --------------------- |
| POST   | `/api/auth/registration/`          | Register new user     |
| POST   | `/api/auth/login/`                 | Login                 |
| POST   | `/api/auth/logout/`                | Logout                |
| GET    | `/api/auth/user/`                  | Get user profile      |
| POST   | `/api/auth/token/refresh/`         | Refresh token         |
| POST   | `/api/auth/token/verify/`          | Verify token          |
| POST   | `/api/auth/social/google/`         | Google login          |
| POST   | `/api/auth/social/github/`         | GitHub login          |
| POST   | `/api/auth/social/token-exchange/` | Exchange social token |

## 🔒 Security Features

✅ JWT access & refresh tokens  
✅ Token rotation on refresh  
✅ Token blacklisting on logout  
✅ Password validation  
✅ CORS protection  
✅ Environment variable security

## 💡 Tips

-   Access tokens expire in 60 minutes (configurable in `.env`)
-   Refresh tokens expire in 24 hours (configurable in `.env`)
-   All tokens are automatically rotated on refresh
-   Tokens are blacklisted on logout for security

## 🐛 Troubleshooting

**Server not starting?**

```bash
source venv/bin/activate
python manage.py migrate
python manage.py runserver
```

**CORS errors?**

-   Add your frontend URL to `CORS_ALLOWED_ORIGINS` in `.env`

**Social login not working?**

-   Make sure OAuth credentials are set in `.env`
-   Verify redirect URIs in OAuth provider settings

## 📞 Need Help?

Check the detailed documentation in `AUTH_README.md`

---

**Server Status:** ✅ Running at http://127.0.0.1:8000/  
**Admin Panel:** http://127.0.0.1:8000/admin/  
**API Base:** http://127.0.0.1:8000/api/auth/
