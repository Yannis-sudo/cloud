# Cloud Backend API Documentation

Welcome to the comprehensive documentation for the Cloud Backend API. This modern, modular backend provides authentication, email management, notes management, file storage, and more.

## Quick Start

### Prerequisites
- Python 3.8+
- MongoDB 4.4+
- FastAPI and related dependencies

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd backend

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run the application
python -m app.main
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
|   |-- api/                   # API layer (routes)
|   |-- core/                  # Core business logic
|   |-- modules/               # Business modules
|   |-- database/             # Database layer
|   |-- schemas/              # Pydantic schemas
|   |-- utils/               # Utilities
|   |-- dependencies.py      # Dependency injection
|   |-- main.py              # FastAPI app
|   `-- config.py            # Configuration
```

## Key Features

- **JWT Authentication**: Secure token-based authentication with refresh tokens
- **Modular Design**: Clean separation of concerns for maintainability
- **GridFS Storage**: Scalable file storage using MongoDB GridFS
- **API Versioning**: Backward-compatible API versioning
- **Comprehensive Error Handling**: Standardized error responses
- **Type Safety**: Full type hints throughout the codebase

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. All protected endpoints require a valid access token in the Authorization header:

```
Authorization: Bearer <access_token>
```

### Token Flow
1. **Login**: Get access and refresh tokens
2. **Access Token**: Used for API calls (30-minute expiry)
3. **Refresh Token**: Used to get new access tokens (7-day expiry)

## API Endpoints

### Authentication (`/api/v1/auth`)
- `POST /login` - Authenticate user
- `POST /register` - Register new user
- `POST /refresh` - Refresh access token
- `POST /logout` - Logout user
- `POST /password-reset-request` - Request password reset
- `POST /password-reset-confirm` - Confirm password reset
- `POST /change-password` - Change password
- `GET /me` - Get current user info

### Accounts (`/api/v1/accounts`)
- `GET /profile` - Get user profile

### Emails (`/api/v1/emails`)
- `GET /servers` - Get email server configurations

### Notes (`/api/v1/notes`)
- `GET /lists` - Get notes lists

### Files (`/api/v1/files`)
- `POST /upload` - Upload file

### Users (`/api/v1/users`)
- `GET /search` - Search users

### Health (`/api/v1/health`)
- `GET /health` - Detailed health check

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

### Common Error Codes
- `VALIDATION_ERROR` (422) - Invalid input data
- `UNAUTHORIZED` (401) - Authentication required
- `FORBIDDEN` (403) - Access denied
- `NOT_FOUND` (404) - Resource not found
- `CONFLICT` (409) - Resource already exists
- `RATE_LIMIT_EXCEEDED` (429) - Too many requests

## Development

### Running Tests
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=app
```

### Code Style
The project follows PEP 8 and uses type hints throughout. Run linting with:
```bash
python -m flake8 app/
python -m mypy app/
```

### Database Migrations
```bash
# Run migrations
python -m app.database.migrations.run

# Create new migration
python -m app.database.migrations.create <migration_name>
```

## Security

- **Password Hashing**: Uses bcrypt for secure password storage
- **JWT Tokens**: Secure token-based authentication
- **Input Validation**: Comprehensive input validation using Pydantic
- **Rate Limiting**: Protection against brute force attacks
- **CORS**: Configurable CORS settings

## Support

For support and questions:
- Check the [API Documentation](./api/README.md)
- Review the [Architecture Guide](./developer/architecture.md)
- See the [Troubleshooting Guide](./ai/troubleshooting.md)

---

*This documentation is continuously updated. Last updated: 2023-01-01*
