# FastAPI Users Authentication Guide

## Overview

This backend has been migrated to use **FastAPI Users** with **Beanie ODM** for MongoDB support, providing a professional, industry-standard authentication system with JWT tokens, email verification, password reset, and OAuth-ready infrastructure.

## Architecture

### Technology Stack

- **FastAPI Users**: Authentication framework
- **Beanie**: Async MongoDB ODM (Object-Document Mapper)
- **Motor**: Async MongoDB driver (used by Beanie under the hood)
- **JWT (HS256)**: Token-based authentication with Bearer transport
- **bcrypt**: Password hashing via **passlib**

### Key Components

```
app/auth/
├── models.py           # Beanie User document model
├── schemas.py          # Pydantic schemas (UserRead, UserCreate, UserUpdate)
├── database.py         # BeanieUserDatabase dependency
├── backend.py          # JWTStrategy configuration
├── manager.py          # UserManager with lifecycle hooks
├── dependencies.py     # Route protection dependencies (get_current_active_user, etc.)
├── routes.py           # FastAPI Users router orchestration
└── __init__.py         # Module exports
```

## User Model

### Fields

The `User` model stores:

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `id` | ObjectId | Unique, auto-generated | MongoDB ObjectId, serialized as string in API |
| `email` | str | Unique, required | Primary login identifier, lowercase |
| `name` | str | Required | Full name (replaces first_name/last_name) |
| `hashed_password` | str | Required | Bcrypt hashed password (100+ chars) |
| `is_active` | bool | Default: True | Account activation status |
| `is_verified` | bool | Default: False | Email verification status |
| `is_superuser` | bool | Default: False | Admin/superuser flag |
| `created_at` | datetime | Auto-set | User creation timestamp |
| `updated_at` | datetime | Auto-set | Last modification timestamp |

### Database Representation

Users are stored in MongoDB as documents in the `users` collection:

```json
{
  "_id": ObjectId("507f1f77bcf86cd799439011"),
  "email": "user@example.com",
  "name": "John Doe",
  "hashed_password": "$2b$12$...",
  "is_active": true,
  "is_verified": false,
  "is_superuser": false,
  "created_at": ISODate("2026-04-10T10:00:00Z"),
  "updated_at": ISODate("2026-04-10T10:00:00Z")
}
```

### Indexes

- **email (unique)**: Ensures email uniqueness and fast lookups
- **name**: Supports filtering/sorting by user name

## Authentication Endpoints

### Registration

**POST** `/api/v1/auth/register`

Register a new user with email, password, and name.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "name": "John Doe"
}
```

**Response (201 Created):**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "email": "user@example.com",
  "name": "John Doe",
  "is_active": true,
  "is_verified": false,
  "is_superuser": false
}
```

**Errors:**
- `400`: Validation error (invalid email, weak password, missing fields)
- `409`: Email already registered
- `422`: Unprocessable entity (invalid data type)

### Login

**POST** `/api/v1/auth/jwt/login`

Authenticate with email and password to receive JWT token.

**Request:**
```json
{
  "username": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Bearer Token Usage:**

Include the token in all subsequent requests:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Errors:**
- `400`: Invalid email/password combination
- `401`: User inactive
- `422`: Unprocessable entity

### Logout

**POST** `/api/v1/auth/jwt/logout`

Invalidate the current session. Requires authentication.

**Response (200 OK):**
```json
{
  "message": "Logout successful"
}
```

### Email Verification (Optional)

**POST** `/api/v1/auth/request-verify-token`

Request an email verification token (if verification enabled).

**Response (200 OK):**
```json
{
  "message": "Verification token sent"
}
```

**POST** `/api/v1/auth/{user_id}/verify`

Verify email with token provided in email.

**Request:**
```json
{
  "token": "verification-token-from-email"
}
```

**Response (200 OK):**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "email": "user@example.com",
  "name": "John Doe",
  "is_active": true,
  "is_verified": true,
  "is_superuser": false
}
```

### Password Reset

**POST** `/api/v1/auth/forgot-password`

Request a password reset token (sent to email).

**Request:**
```json
{
  "email": "user@example.com"
}
```

**Response (200 OK):**
```json
{
  "message": "Password reset link sent to email"
}
```

**POST** `/api/v1/auth/reset-password`

Reset password with token from email.

**Request:**
```json
{
  "token": "reset-token-from-email",
  "password": "NewSecurePassword123!"
}
```

**Response (200 OK):**
```json
{
  "message": "Password reset successful"
}
```

### User Management

**GET** `/api/v1/auth/users/me`

Get current authenticated user profile.

**Response (200 OK):**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "email": "user@example.com",
  "name": "John Doe",
  "is_active": true,
  "is_verified": false,
  "is_superuser": false
}
```

**PATCH** `/api/v1/auth/users/me`

Update current user (e.g., name).

**Request:**
```json
{
  "name": "Jane Doe"
}
```

**Response (200 OK):**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "email": "user@example.com",
  "name": "Jane Doe",
  "is_active": true,
  "is_verified": false,
  "is_superuser": false
}
```

**PATCH** `/api/v1/auth/users/me`

Change password.

**Request:**
```json
{
  "password": "NewPassword123!"
}
```

---

## Authentication Flow

### User Registration Flow

```
┌────────────────┐
│ Client (React) │
└────────┬───────┘
         │ POST /register
         │ { email, password, name }
         ▼
┌─────────────────────────────────┐
│ FastAPI Users Registration      │
│ - Validate email format         │
│ - Hash password with bcrypt     │
│ - Create User document in MDB   │
└────────┬────────────────────────┘
         │ 201 Created
         │ { id, email, name, ... }
         ▼
┌────────────────────────────┐
│ MongoDB users collection   │
│ Document created           │
│ is_verified = false        │
│ is_active = true           │
└────────────────────────────┘
```

### Successful Authentication Flow

```
┌────────────────┐
│ Client (React) │
└────────┬───────┘
         │ POST /jwt/login
         │ { username: email, password }
         ▼
┌──────────────────────────────────┐
│ JWTStrategy Backend              │
│ - Find user by email             │
│ - Verify password hash           │
│ - Generate JWT token             │
│ - Set token lifetime (30 min)    │
└────────┬───────────────────────┘
         │ 200 OK
         │ { access_token, token_type: "bearer" }
         ▼
┌────────────────────────────────┐
│ Client stores token           │
│ (localStorage, sessionStorage)│
│ for future requests           │
└────────────────────────────────┘
```

### Protected Route Access

```
┌────────────────┐
│ Client (React) │
└────────┬───────┘
         │ GET /api/v1/auth/users/me
         │ Authorization: Bearer <token>
         ▼
┌──────────────────────────────────┐
│ FastAPI dependency injection     │
│ get_current_active_user()        │
│ - Parse JWT from Authorization   │
│ - Verify signature               │
│ - Check token expiration         │
│ - Verify user is active          │
└────────┬───────────────────────┘
         │ User valid
         ▼
┌──────────────────────────────────┐
│ Route handler executes           │
│ with current_user injected       │
│ Can access user: id, email, name │
└────────────────────────────────────┘
```

### Expired/Invalid Token Flow

```
┌────────────────┐
│ Client (React) │
└────────┬────────┘
         │ Authorization: Bearer <expired_token>
         ▼
┌──────────────────────────────┐
│ JWT verification fails       │
│ - Token expired              │
│ - Invalid signature          │
│ - Malformed                  │
└────────┬────────────────────┘
         │ 401 Unauthorized
         ▼
┌────────────────────────────────┐
│ Client handles 401             │
│ - Clear stored token           │
│ - Redirect to login page       │
│ - User must re-authenticate    │
└────────────────────────────────┘
```

---

## Using Authentication in Routes

### Protecting a Route with Current User

To protect a route and inject the current authenticated user:

```python
from fastapi import APIRouter, Depends
from app.auth import User, get_current_active_user

router = APIRouter()

@router.get("/profile")
async def get_profile(current_user: User = Depends(get_current_active_user)):
    """Get current user's profile.
    
    Requires: Valid JWT in Authorization header
    Returns: User email, name, and metadata
    """
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "name": current_user.name,
        "is_verified": current_user.is_verified,
        "created_at": current_user.created_at
    }
```

### Optional Authentication

Get current user if authenticated, or None:

```python
from app.auth import User, get_optional_current_user
from typing import Optional

@router.get("/public-data")
async def get_public_data(current_user: Optional[User] = Depends(get_optional_current_user)):
    """Public endpoint that shows different content if authenticated."""
    if current_user:
        return {
            "message": f"Hello {current_user.name}!",
            "is_authenticated": True
        }
    return {
        "message": "Hello guest!",
        "is_authenticated": False
    }
```

### Superuser-Only Route

```python
from app.auth import User, get_current_superuser

@router.delete("/admin/users/{user_id}")
async def delete_user(user_id: str, admin: User = Depends(get_current_superuser)):
    """Delete a user (admin only)."""
    # Only superusers can reach this route
    return {"deleted": user_id}
```

### Current User Access in Business Logic

```python
from app.auth import User

async def send_email_notification(user: User, subject: str, body: str):
    """Send notification to user email."""
    # Use user.email, user.name, user.id
    print(f"Sending to {user.email}: {subject}")
```

---

## Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=mongodb://localhost:27017
DATABASE_NAME=cloud

# JWT Settings
JWT_SECRET=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_SECONDS=1800  # 30 minutes

# Email Verification (optional)
EMAIL_VERIFICATION_ENABLED=false
ALLOW_UNVERIFIED_EMAIL_LOGIN=true

# OAuth (placeholders for future)
OAUTH_GOOGLE_CLIENT_ID=
OAUTH_GITHUB_CLIENT_ID=
```

### Settings Class

All config loaded from [app/config.py](../app/config.py):

```python
class Settings:
    JWT_SECRET: str           # Token signing secret
    JWT_ALGORITHM: str        # Algorithm (HS256)
    JWT_EXPIRATION_SECONDS: int  # Token lifetime in seconds
    EMAIL_VERIFICATION_ENABLED: bool  # Require email verification
    ALLOW_UNVERIFIED_EMAIL_LOGIN: bool  # Allow login without verification
```

---

## Security Considerations

### Password Hashing

- **Method**: bcrypt via **passlib**
- **Cost Factor**: 12 rounds (default, high security)
- **Stored**: Never store plaintext passwords; only hashed values in MongoDB

### JWT Tokens

- **Type**: HS256 (HMAC with SHA-256)
- **Secret**: Must be strong, stored in `JWT_SECRET` env var
- **Lifetime**: 30 minutes (configurable via `JWT_EXPIRATION_SECONDS`)
- **Transport**: Bearer token in `Authorization` header
- **Signature Verification**: Invalid tokens rejected automatically

### Rate Limiting (Future)

Currently no built-in rate limiting on auth endpoints. Consider adding:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/auth/jwt/login")
@limiter.limit("5/minute")
async def login(...):
    ...
```

### HTTPS (Production)

- Always use HTTPS in production to prevent token interception
- Set `secure=True` in cookie settings (if using cookies)
- Use strong `JWT_SECRET` (min 32 chars, random)

---

## Adding OAuth Later

The authentication infrastructure is **OAuth-ready**. OAuth support is designed into the structure but not yet implemented.

### Future OAuth Integration Steps

1. **Install OAuth dependencies**:
```bash
pip install httpx aiofiles
```

2. **Create provider backends** (`app/auth/oauth/` folder):
```python
# app/auth/oauth/google.py
from fastapi_users.authentication import AuthenticationBackend

google_oauth_backend = AuthenticationBackend(...)
```

3. **Add OAuth routes in FastAPI Users**:
```python
app.include_router(
    fastapi_users.get_oauth_router(google_oauth_client, ...)
)
```

4. **Environment variables**:
```bash
OAUTH_GOOGLE_CLIENT_ID=your-client-id
OAUTH_GOOGLE_CLIENT_SECRET=your-client-secret
```

See [FastAPI Users OAuth Documentation](https://fastapi-users.github.io/fastapi-users/latest/configuration/oauth/) for complete examples.

---

## Adding Email Verification

Email verification is built-in via FastAPI Users but disabled by default.

### Enable Email Verification

1. **Set env var**:
```bash
EMAIL_VERIFICATION_ENABLED=true
```

2. **Configure email backend** (future):
```python
# app/auth/email.py
from fastapi_users import FastAPIUsers

async def on_after_register(user: User, request: Optional[Request]):
    """Send verification email after registration."""
    verification_url = f"https://app.example.com/verify?token={...}"
    await send_verification_email(user.email, verification_url)
```

3. **User flow**:
   - User registers → `is_verified = false`
   - Verification email sent with link
   - User clicks link → calls `/api/v1/auth/{id}/verify`
   - `is_verified = true`
   - Can now login

---

## Adding 2FA/MFA (Future)

FastAPI Users has support for 2FA via TOTP (Time-based One-Time Password).

### Future 2FA Implementation

1. **Install dependencies**:
```bash
pip install pyotp qrcode
```

2. **Extend User model**:
```python
class User(BeanieBaseUser, Document):
    totp_secret: Optional[str] = None
    totp_enabled: bool = False
```

3. **Add 2FA routes**:
   - `POST /auth/2fa/enable` — Generate TOTP secret
   - `POST /auth/2fa/verify` — Confirm TOTP setup
   - `POST /auth/2fa/disable` — Disable TOTP

4. **Modify login flow**:
   - After password verification, check if 2FA enabled
   - Request TOTP code
   - Verify and issue JWT

---

## Database Migrations

### Creating Indexes

Beanie handles index creation automatically on startup. The `users` collection will have:

```javascript
// Email uniqueness
db.users.createIndex({ email: 1 }, { unique: true })

// Name filtering/sorting
db.users.createIndex({ name: 1 })
```

### Existing User Migration (If needed)

If upgrading from old auth system, migrate existing users:

```python
# Migration script (one-time)
from app.database.async_db import get_database
from app.auth.models import User
from beanie import Document
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def migrate_users():
    """Migrate existing users from old collection."""
    db = await get_database()
    old_users = db["old_users_collection"].find()
    
    async for old_user in old_users:
        user = User(
            email=old_user["email"],
            name=f"{old_user.get('first_name', '')} {old_user.get('last_name', '')}".strip(),
            hashed_password=old_user["password"],  # Already hashed
            is_active=old_user.get("is_active", True),
            is_verified=old_user.get("is_verified", False),
        )
        await user.save()
```

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| `401 Unauthorized` | Invalid/expired token | Re-login, get new token |
| `422 Unprocessable Entity` | Invalid request data | Check email format, password length |
| `409 Conflict` | Email already registered | Use different email or password reset |
| `500 Database Error` | MongoDB connection issue | Check `DATABASE_URL`, MongoDB is running |
| `Beanie not initialized` | Models not registered on startup | Verify `init_db([User])` in lifespan |

### Debugging

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Check logs for:
- MongoDB connection errors
- Beanie initialization
- JWT token signature failures
- Database permission issues

---

## Related Documentation

- [FastAPI Users Official Docs](https://fastapi-users.github.io/)
- [Beanie ODM Docs](https://beanie-odm.readthedocs.io/)
- [Motor Async MongoDB Driver](https://motor.readthedocs.io/)
- [JWT Standards](https://tools.ietf.org/html/rfc7519)
- [Backend Security Checklist](../developer/security.md) (link if it exists)
