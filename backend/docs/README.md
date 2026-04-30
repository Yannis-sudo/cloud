# Cloud Backend API Documentation

Welcome to the comprehensive documentation for the Cloud Backend API. This modern, modular backend provides authentication, AI chat capabilities, and more.

## Quick Start

### Prerequisites
- Python 3.10+
- MongoDB 6.0+
- FastAPI and related dependencies

### Installation
```bash
# Navigate to backend directory
cd cloud/backend

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run the application
python -m uvicorn app.main:app --reload --port 5555
```

### API Base URL
```
http://localhost:5555/api/v1
```

## Architecture Overview

This backend follows a clean, modular architecture with clear separation of concerns:

```
backend/
|-- app/
|   |-- api/v1/              # API layer (routes)
|   |-- auth/                # Authentication module
|   |-- core/                # Core business logic & exceptions
|   |-- modules/            # Business modules (ai_chats, users)
|   |-- database/           # Database layer (async & sync)
|   |-- schemas/            # Pydantic schemas
|   |-- utils/              # Utilities
|   |-- dependencies.py     # Dependency injection
|   |-- main.py             # FastAPI app
|   `-- config.py           # Configuration
|-- docs/                   # Documentation
`-- requirements.txt        # Python dependencies
```

## Key Features

- **JWT Authentication**: Secure token-based authentication using FastAPI Users
- **Beanie ODM**: MongoDB object-document mapping with async support
- **Modular Design**: Clean separation of concerns for maintainability
- **API Versioning**: Backward-compatible API versioning (v1)
- **Comprehensive Error Handling**: Standardized error responses
- **Type Safety**: Full type hints throughout the codebase
- **AI Model Management**: User-specific AI model permissions

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. All protected endpoints require a valid access token in the Authorization header:

```
Authorization: Bearer <access_token>
```

### Token Flow
1. **Login**: POST to `/api/v1/auth/jwt/login` with email/password
2. **Access Token**: Used for API calls (30-minute default expiry)
3. **Protected Endpoints**: Include token in Authorization header

## API Endpoints

### Authentication (`/api/v1/auth`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /jwt/login | Authenticate user |
| POST | /jwt/logout | Logout user |
| POST | /register | Register new user |
| POST | /verify | Verify email |
| POST | /forgot-password | Request password reset |
| POST | /reset-password | Reset password |
| GET | /users/me | Get current user |
| PATCH | /users/me | Update current user |

### AI Chat (`/api/v1/ai-chat`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /available-models | Get user's available AI models |

### Health (`/api/v1/health`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /health | Detailed health check |

## Database Models

### User
- `id`: ObjectId (unique identifier)
- `email`: str (unique, required)
- `username`: str (full name)
- `hashed_password`: str
- `is_active`: bool
- `is_superuser`: bool
- `is_verified`: bool

### UserAIModels
- `user_id`: ObjectId (reference to User)
- `models`: List[ModelInfo] (allowed AI models)

### ModelCatalog
- `type`: str (e.g., 'free-models')
- `models`: List[ModelInfo] (available models)

## Error Handling

The API uses standardized error responses:

```json
{
  "success": false,
  "message": "Error description",
  "error_code": "ERROR_TYPE",
  "details": {},
  "timestamp": "2023-01-01T00:00:00Z"
}
```

### Custom Exceptions
- `AuthenticationError` (401) - Authentication failed
- `AuthorizationError` (403) - Access denied
- `ValidationError` (422) - Invalid input data
- `NotFoundError` (404) - Resource not found
- `ConflictError` (409) - Resource already exists
- `DatabaseError` (500) - Database operation failed
- `RateLimitError` (429) - Too many requests

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | MongoDB connection string | mongodb://localhost:27017 |
| DATABASE_NAME | Database name | cloud |
| JWT_SECRET | Secret key for JWT tokens | (change in production) |
| JWT_ALGORITHM | JWT algorithm | HS256 |
| JWT_EXPIRATION_SECONDS | Token expiry | 1800 (30 min) |
| CORS_ORIGINS | Allowed CORS origins | localhost:5173 |
| ALLOW_ALL_ORIGINS | Allow all origins | false |
| MAX_FILE_SIZE | Max upload size (bytes) | 10485760 (10MB) |

## Development

### Running Tests
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=app
```

### Code Style
The project follows PEP 8 and uses type hints. Run linting with:
```bash
python -m flake8 app/
python -m mypy app/
```

## Security

- **Password Hashing**: Uses bcrypt for secure password storage
- **JWT Tokens**: Secure token-based authentication
- **Input Validation**: Comprehensive input validation using Pydantic
- **CORS**: Configurable CORS settings

---

*This documentation is continuously updated. Last updated: April 2026*
