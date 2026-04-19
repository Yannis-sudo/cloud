# FastAPI Users Authentication - Quick Start & Testing Guide

**Implementation Date**: April 10, 2026  
**Status**: ✅ Ready for deployment

---

## What You Get

Your backend now has a **professional, production-ready authentication system** using FastAPI Users with MongoDB/Beanie. This includes:

### ✅ Completed Requirements

| Requirement | Status | File/Location |
|-------------|--------|---------------|
| **1. Install/Configure Dependencies** | ✅ | requirements.txt updated with fastapi-users[beanie], beanie, motor |
| **2. Create Auth Module Structure** | ✅ | New `app/auth/` folder with 8 files |
| **3. User MongoDB Model** | ✅ | [app/auth/models.py](app/auth/models.py) - id, email, name, hashed_password, is_active, is_superuser, is_verified |
| **4. Database Integration** | ✅ | [app/database/async_db.py](app/database/async_db.py) - Motor + Beanie async setup |
| **5. JWT Authentication Backend** | ✅ | [app/auth/backend.py](app/auth/backend.py) - HS256, 30-min configurable |
| **6. Auth Routes** | ✅ | [app/auth/routes.py](app/auth/routes.py) - /login, /register, /verify, /forgot-password, /reset-password |
| **7. Current User Dependency** | ✅ | [app/auth/dependencies.py](app/auth/dependencies.py) - get_current_active_user, get_current_superuser |
| **8. Config/Environment** | ✅ | [app/config.py](app/config.py) + [.env](.env) - JWT_SECRET, JWT_EXPIRATION_SECONDS |
| **9. Keep Existing Code Compatible** | ✅ | No breaking changes; old auth code archived but not used |
| **10. Output/Documentation** | ✅ | [docs/auth-fastapi-users-guide.md](docs/auth-fastapi-users-guide.md) + [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) |
| **BONUS: Add "name" field** | ✅ | [app/auth/models.py](app/auth/models.py) - Single "name" field replacing first_name/last_name |

---

## Quick Demo

### 1. Start the Backend

```bash
cd /home/yannis/dev/cloud

# Build and run with Docker
docker-compose up --build

# Wait for:
# ✓ Async MongoDB (Motor) connection established successfully
# ✓ Beanie initialized successfully with all document models
# ✓ Application startup completed
```

### 2. Register a User

```bash
curl -X POST http://localhost:5555/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@example.com",
    "password": "DemoPassword123!",
    "name": "Demo User"
  }'
```

**Response (201 Created)**:
```json
{
  "id": "507f1f77bcf86cd799439011",
  "email": "demo@example.com",
  "name": "Demo User",
  "is_active": true,
  "is_verified": false,
  "is_superuser": false
}
```

### 3. Login

```bash
curl -X POST http://localhost:5555/api/v1/auth/jwt/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo@example.com",
    "password": "DemoPassword123!"
  }'
```

**Response (200 OK)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 4. Use Token on Protected Routes

```bash
# Save token from login response
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Get current user profile
curl -X GET http://localhost:5555/api/v1/auth/users/me \
  -H "Authorization: Bearer $TOKEN"
```

**Response (200 OK)**:
```json
{
  "id": "507f1f77bcf86cd799439011",
  "email": "demo@example.com",
  "name": "Demo User",
  "is_active": true,
  "is_verified": false,
  "is_superuser": false
}
```

### 5. Try Protected Endpoint

Update user name:

```bash
curl -X PATCH http://localhost:5555/api/v1/auth/users/me \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Name"}'
```

---

## API Documentation

### Interactive Swagger UI

Once running, visit: **http://localhost:5555/docs**

- Try all endpoints interactively
- See request/response schemas
- Authorize with Bearer token directly in UI

### ReDoc Alternative

**http://localhost:5555/redoc** - Read-only docs view

---

## Available Endpoints

All at `/api/v1/auth/`:

| Method | Path | Purpose | Requires Auth |
|--------|------|---------|---------------|
| **POST** | `/register` | Register new user | ❌ |
| **POST** | `/jwt/login` | Login (email + password → JWT) | ❌ |
| **POST** | `/jwt/logout` | Logout | ✅ |
| **GET** | `/users/me` | Get profile | ✅ |
| **PATCH** | `/users/me` | Update profile (name) | ✅ |
| **POST** | `/request-verify-token` | Send verification email | ❌ |
| **POST** | `/{id}/verify` | Verify email | ❌ |
| **POST** | `/forgot-password` | Send password reset email | ❌ |
| **POST** | `/reset-password` | Reset password | ❌ |

---

## Using Auth in Your Routes

### Protect a Route

```python
from fastapi import APIRouter, Depends
from app.auth import User, get_current_active_user

router = APIRouter()

@router.get("/my-data")
async def get_my_data(current_user: User = Depends(get_current_active_user)):
    """Only authenticated users can access this."""
    return {
        "user_id": str(current_user.id),
        "user_name": current_user.name,
        "user_email": current_user.email,
    }
```

### Optional Auth

```python
from typing import Optional
from app.auth import User, get_optional_current_user

@router.get("/public")
async def public_route(current_user: Optional[User] = Depends(get_optional_current_user)):
    if current_user:
        return {"greeting": f"Hello {current_user.name}!"}
    return {"greeting": "Hello guest!"}
```

### Admin Only

```python
from app.auth import User, get_current_superuser

@router.delete("/admin/delete")
async def delete_something(admin: User = Depends(get_current_superuser)):
    """Only superusers (is_superuser=True) can access."""
    return {"deleted": True}
```

---

## Configuration

### Environment Variables

**Required** (set in `.env`):
```bash
DATABASE_URL=mongodb://localhost:27017
DATABASE_NAME=cloud
JWT_SECRET=your-super-secret-key-min-32-chars-change-this
```

**Optional** (defaults provided):
```bash
JWT_ALGORITHM=HS256                    # Don't change unless needed
JWT_EXPIRATION_SECONDS=1800            # 30 minutes
EMAIL_VERIFICATION_ENABLED=false       # Enable if you add email service
ALLOW_UNVERIFIED_EMAIL_LOGIN=true      # Allow login before verification
```

### Changing Token Lifetime

Token expires after 30 minutes by default. To change:

```bash
# In .env
JWT_EXPIRATION_SECONDS=3600  # 1 hour
JWT_EXPIRATION_SECONDS=86400  # 1 day
```

### Enabling Email Verification

1. Set in `.env`:
```bash
EMAIL_VERIFICATION_ENABLED=true
```

2. Implement email sending in [app/auth/manager.py](app/auth/manager.py):
```python
async def on_after_verification_request(
    self, user: User, token: str, request: Optional[object] = None
) -> None:
    # Send verification email with token link
    await send_verification_email(user.email, token)
```

---

## Next: Integrating Into Existing Routes

### Example: Protect Notes Endpoint

**Old code** (if using custom auth):
```python
# NOT USED ANYMORE
from app.core.auth import verify_token
from app.dependencies import get_current_user

@router.get("/notes")
async def list_notes(current_user = Depends(get_current_user)):
    ...
```

**New code** (using FastAPI Users):
```python
from app.auth import User, get_current_active_user

@router.get("/notes")
async def list_notes(current_user: User = Depends(get_current_active_user)):
    # Same signature, better infrastructure
    # current_user is now a proper User object with email, name, id, etc.
    return {"user_id": str(current_user.id), "notes": [...]}
```

---

## Testing with Your Frontend

### React Example

```javascript
// Register
async function register(email, password, name) {
  const res = await fetch('http://localhost:5555/api/v1/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, name })
  });
  return res.json();
}

// Login
async function login(email, password) {
  const res = await fetch('http://localhost:5555/api/v1/auth/jwt/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: email, password })
  });
  const data = await res.json();
  localStorage.setItem('token', data.access_token);
  return data;
}

// Get Profile
async function getProfile() {
  const token = localStorage.getItem('token');
  const res = await fetch('http://localhost:5555/api/v1/auth/users/me', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return res.json();
}
```

---

## Troubleshooting

### 401 Unauthorized

- Token expired? Re-login
- Missing Authorization header?
- Invalid token format? Must be: `Authorization: Bearer <token>`

### 422 Unprocessable Entity

- Email validation failed? Check email format
- Password too short? Must be 8+ characters
- Missing required field? Check request body

### 409 Conflict (Email already registered)

- Use a different email
- Or reset database and re-register

### 500 Database Error

- MongoDB not running? Check docker-compose
- Connection string wrong? Verify DATABASE_URL
- Check logs: `docker-compose logs backend`

See [Full Troubleshooting Guide](docs/auth-fastapi-users-guide.md#troubleshooting)

---

## Files Modified/Created

### New:
- `app/auth/` (8 files) — Complete auth module
- `app/database/async_db.py` — Async MongoDB setup
- `docs/auth-fastapi-users-guide.md` — Full guide
- `IMPLEMENTATION_SUMMARY.md` — Summary of changes

### Modified:
- `requirements.txt` — New dependencies
- `app/config.py` — JWT settings
- `app/main.py` — Beanie init, router mounting
- `.env` — JWT environment variables

---

## Next Steps

1. ✅ **Run with Docker**: `docker-compose up --build`
2. ✅ **Test endpoints**: Use curl or Swagger UI at `/docs`
3. ⚠️ **Update existing routes**: Replace old auth imports with new dependencies (optional, gradual)
4. 🔄 **Add OAuth**: When ready, follow [OAuth Integration Guide](docs/auth-fastapi-users-guide.md#adding-oauth-later)
5. 📧 **Add Email Verification**: When ready, configure email service
6. 2️⃣ **Add 2FA**: When ready, follow [2FA Guide](docs/auth-fastapi-users-guide.md#adding-2famfa-future)

---

## Support

- **Full Documentation**: [docs/auth-fastapi-users-guide.md](docs/auth-fastapi-users-guide.md)
- **Implementation Details**: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
- **FastAPI Users Docs**: https://fastapi-users.github.io/
- **Beanie Docs**: https://beanie-odm.readthedocs.io/

---

**Status**: ✅ Ready to deploy. Run `docker-compose up --build` to start!
