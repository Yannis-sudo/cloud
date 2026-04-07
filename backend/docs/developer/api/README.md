# API Documentation

This section provides detailed documentation for all API endpoints.

## Base URL
```
http://localhost:5555/api/v1
```

## Authentication

All endpoints (except authentication endpoints) require a valid JWT token in the Authorization header:

```
Authorization: Bearer <access_token>
```

### Token Types
- **Access Token**: Short-lived (30 minutes) for API calls
- **Refresh Token**: Long-lived (7 days) for getting new access tokens

## Endpoints

### Authentication Endpoints

#### POST /auth/login
Authenticate a user and return tokens.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "message": "Login successful",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "username": "john_doe",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_active": true,
    "is_verified": true,
    "created_at": "2023-01-01T00:00:00Z",
    "last_login": "2023-01-15T12:30:00Z"
  },
  "tokens": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
```

**Error Responses:**
- `401` - Invalid credentials
- `422` - Validation error

---

#### POST /auth/register
Register a new user and return tokens.

**Request:**
```json
{
  "username": "john_doe",
  "email": "user@example.com",
  "password": "password123",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response:**
Same as login response with `message: "Registration successful"`

**Error Responses:**
- `409` - User already exists
- `422` - Validation error

---

#### POST /auth/refresh
Refresh access token using refresh token.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Error Responses:**
- `401` - Invalid refresh token

---

#### POST /auth/logout
Logout user by invalidating refresh token.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:**
```json
{
  "message": "Logout successful"
}
```

---

#### POST /auth/password-reset-request
Request password reset token.

**Request:**
```json
{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "message": "If the email exists, a password reset link has been sent"
}
```

---

#### POST /auth/password-reset-confirm
Reset password using reset token.

**Request:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "new_password": "newpassword123"
}
```

**Response:**
```json
{
  "message": "Password reset successful"
}
```

---

#### POST /auth/change-password
Change user password (requires authentication).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "current_password": "oldpassword123",
  "new_password": "newpassword123"
}
```

**Response:**
```json
{
  "message": "Password changed successfully"
}
```

---

#### GET /auth/me
Get current authenticated user information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "success": true,
  "message": "User information retrieved successfully",
  "data": {
    "id": "507f1f77bcf86cd799439011",
    "username": "john_doe",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_active": true,
    "is_verified": true,
    "created_at": "2023-01-01T00:00:00Z",
    "last_login": "2023-01-15T12:30:00Z"
  }
}
```

---

### Account Endpoints

#### GET /accounts/profile
Get user profile information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "success": true,
  "message": "Profile retrieved successfully",
  "data": {
    "user_id": "507f1f77bcf86cd799439011",
    "email": "user@example.com"
  }
}
```

---

### Email Endpoints

#### GET /emails/servers
Get user's configured email servers.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "success": true,
  "message": "Email servers retrieved successfully",
  "data": {
    "servers": [
      {
        "id": "507f1f77bcf86cd799439011",
        "email": "user@example.com",
        "server_incoming": "imap.gmail.com",
        "server_outgoing": "smtp.gmail.com",
        "server_incoming_port": 993,
        "server_outgoing_port": 587,
        "is_active": true,
        "last_sync": "2023-01-15T12:30:00Z"
      }
    ]
  }
}
```

---

### Notes Endpoints

#### GET /notes/lists
Get user's notes lists.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "success": true,
  "message": "Notes lists retrieved successfully",
  "data": {
    "lists": [
      {
        "id": "507f1f77bcf86cd799439011",
        "list_name": "Project Tasks",
        "description": "Tasks for current project",
        "creator_email": "user@example.com",
        "is_active": true,
        "created_at": "2023-01-01T00:00:00Z",
        "members": ["user@example.com", "collaborator@example.com"]
      }
    ]
  }
}
```

---

### Files Endpoints

#### POST /files/upload
Upload a file to GridFS storage.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Request:**
```
file: <binary file data>
```

**Response:**
```json
{
  "success": true,
  "message": "File uploaded successfully",
  "data": {
    "filename": "document.pdf",
    "size": 1024000,
    "content_type": "application/pdf",
    "file_id": "507f1f77bcf86cd799439011"
  }
}
```

**Error Responses:**
- `413` - File too large
- `422` - Invalid file type

---

### Users Endpoints

#### GET /users/search
Search for users by username or email.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `query` (string) - Search term
- `limit` (integer, optional) - Maximum results (default: 10)

**Response:**
```json
{
  "success": true,
  "message": "Users search completed",
  "data": {
    "query": "john",
    "results": [
      {
        "id": "507f1f77bcf86cd799439011",
        "username": "john_doe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe"
      }
    ]
  }
}
```

---

### Health Endpoints

#### GET /health
Detailed health check of all services.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "database": "healthy",
    "email_service": "healthy",
    "file_storage": "healthy"
  },
  "timestamp": "2023-01-01T00:00:00Z"
}
```

---

## Error Responses

All error responses follow this format:

```json
{
  "success": false,
  "message": "Error description",
  "error_code": "ERROR_TYPE",
  "details": {},
  "timestamp": "2023-01-01T00:00:00Z"
}
```

### Common Error Codes

| Status Code | Error Code | Description |
|-------------|------------|-------------|
| 400 | BAD_REQUEST | Invalid request format |
| 401 | UNAUTHORIZED | Authentication required |
| 403 | FORBIDDEN | Access denied |
| 404 | NOT_FOUND | Resource not found |
| 409 | CONFLICT | Resource already exists |
| 422 | VALIDATION_ERROR | Invalid input data |
| 429 | RATE_LIMIT_EXCEEDED | Too many requests |
| 500 | INTERNAL_SERVER_ERROR | Server error |

### Validation Errors

For validation errors, the response includes detailed field errors:

```json
{
  "success": false,
  "message": "Validation failed",
  "error_code": "VALIDATION_ERROR",
  "validation_errors": [
    {
      "field": "email",
      "message": "Invalid email format",
      "value": "invalid-email"
    },
    {
      "field": "password",
      "message": "Password must be at least 6 characters",
      "value": "123"
    }
  ],
  "timestamp": "2023-01-01T00:00:00Z"
}
```

## Rate Limiting

API endpoints are rate-limited to prevent abuse:

- **Authentication endpoints**: 5 requests per minute
- **General endpoints**: 100 requests per hour
- **File uploads**: 10 requests per hour

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## Pagination

Endpoints that return lists support pagination:

**Query Parameters:**
- `page` (integer) - Page number (default: 1)
- `limit` (integer) - Items per page (default: 20, max: 100)

**Response:**
```json
{
  "success": true,
  "message": "Data retrieved successfully",
  "data": [],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "pages": 5,
    "has_next": true,
    "has_prev": false
  }
}
```

## SDK Examples

### Python
```python
import requests

# Login
response = requests.post("http://localhost:5555/api/v1/auth/login", json={
    "email": "user@example.com",
    "password": "password123"
})
tokens = response.json()["tokens"]

# Use access token
headers = {"Authorization": f"Bearer {tokens['access_token']}"}
response = requests.get("http://localhost:5555/api/v1/auth/me", headers=headers)
user = response.json()["data"]
```

### JavaScript
```javascript
// Login
const response = await fetch('http://localhost:5555/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password123'
  })
});
const { tokens } = await response.json();

// Use access token
const userResponse = await fetch('http://localhost:5555/api/v1/auth/me', {
  headers: { 'Authorization': `Bearer ${tokens.access_token}` }
});
const { data: user } = await userResponse.json();
```

---

For more examples and advanced usage, see the [Examples](../examples/) section.
