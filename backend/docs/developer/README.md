# Developer Guide

This guide is for developers who want to understand, maintain, and extend the Cloud Backend API.

## Architecture Overview

The backend follows a clean, layered architecture:

### 1. API Layer (`app/api/`)
Handles HTTP requests and responses. Organized by version (v1).

**Key Principles:**
- Thin controllers - only handle HTTP concerns
- Use dependency injection for services
- Standardized error handling
- Input validation using Pydantic schemas

**Example:**
```python
@router.post("/login")
async def login(request: LoginRequest) -> LoginResponse:
    try:
        result = await auth_service.login(request.email, request.password)
        return LoginResponse(**result)
    except Exception as e:
        handle_auth_error(e)
```

### 2. Core Layer (`app/core/`)
Contains core business logic and cross-cutting concerns.

**Components:**
- `auth.py` - Authentication business logic
- `security.py` - Security utilities (JWT, password hashing)
- `exceptions.py` - Custom exception classes
- `middleware.py` - Core middleware functions

### 3. Modules Layer (`app/modules/`)
Business logic organized by feature domain.

**Structure:**
```
modules/
|-- accounts/     # User account management
|-- emails/        # Email operations
|-- notes/         # Notes management
|-- files/         # File operations
`-- users/         # User management
```

Each module contains:
- `service.py` - Business logic
- `models.py` - Data models
- `validators.py` - Input validation

### 4. Database Layer (`app/database/`)
Data access layer using Repository pattern.

**Components:**
- `connection.py` - Database connection management
- `repositories/` - Data access objects
- `migrations/` - Database migrations

## Development Setup

### 1. Environment Setup
```bash
# Clone repository
git clone <repo-url>
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your settings
```

### 2. Database Setup
```bash
# Start MongoDB
mongod

# Run migrations
python -m app.database.migrations.run

# Create indexes
python -m app.database.indexes.create_all
```

### 3. Running the Application
```bash
# Development mode
python -m app.main

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 5555
```

## Code Conventions

### 1. Type Hints
All functions must have type hints:

```python
async def create_user(
    username: str,
    email: str,
    password: str
) -> Dict[str, Any]:
    """Create a new user."""
    pass
```

### 2. Error Handling
Use custom exceptions for business logic errors:

```python
from app.core.exceptions import ValidationError, NotFoundError

if not email:
    raise ValidationError("Email is required")

if not user:
    raise NotFoundError("User not found")
```

### 3. Repository Pattern
Always use repositories for database operations:

```python
from app.database.repositories.users import UserRepository

class UserService:
    def __init__(self):
        self.user_repository = UserRepository()
    
    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        return await self.user_repository.get_by_id(user_id)
```

### 4. Dependency Injection
Use FastAPI's dependency injection:

```python
from app.dependencies import get_current_user, get_user_service

@router.get("/profile")
async def get_profile(
    current_user: TokenData = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    pass
```

## Adding New Features

### 1. Create New Module
```bash
mkdir app/modules/new_feature
touch app/modules/new_feature/{__init__.py,service.py,models.py,validators.py}
```

### 2. Create Repository
```python
# app/database/repositories/new_feature.py
from app.database.repositories.base import BaseRepository

class NewFeatureRepository(BaseRepository):
    def __init__(self):
        super().__init__("new_feature_collection")
    
    def get_model_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {}}
```

### 3. Create Service
```python
# app/modules/new_feature/service.py
class NewFeatureService:
    def __init__(self):
        self.repository = NewFeatureRepository()
    
    async def create_item(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Business logic here
        return await self.repository.create(data)
```

### 4. Create API Endpoints
```python
# app/api/v1/new_feature.py
from fastapi import APIRouter, Depends

router = APIRouter()

@router.post("/items")
async def create_item(
    request: CreateItemRequest,
    service: NewFeatureService = Depends(get_new_feature_service)
):
    item = await service.create_item(request.dict())
    return SuccessResponse(data=item)
```

### 5. Update Main App
```python
# app/main.py
from app.api.v1 import new_feature

app.include_router(
    new_feature.router,
    prefix="/api/v1/new-feature",
    tags=["new_feature"]
)
```

## Testing

### 1. Unit Tests
```python
# tests/test_user_service.py
import pytest
from app.modules.users.service import UserService

@pytest.mark.asyncio
async def test_create_user():
    service = UserService()
    user = await service.create_user(
        username="test",
        email="test@example.com",
        password="password123"
    )
    assert user["username"] == "test"
```

### 2. Integration Tests
```python
# tests/test_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_login():
    response = client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
```

### 3. Running Tests
```bash
# All tests
pytest

# With coverage
pytest --cov=app

# Specific test
pytest tests/test_user_service.py::test_create_user
```

## Database Operations

### 1. Using Repositories
```python
# Create
user_id = await user_repository.create_user(
    username="john",
    email="john@example.com",
    password="hashed_password"
)

# Read
user = await user_repository.get_by_id(user_id)
users = await user_repository.get_many({"is_active": True})

# Update
await user_repository.update(user_id, {"last_login": datetime.utcnow()})

# Delete
await user_repository.delete(user_id)
```

### 2. Transactions
```python
from app.database.connection import get_transaction

async def transfer_data():
    async with get_transaction() as session:
        # Multiple operations in transaction
        await repo1.create(data1, session=session)
        await repo2.update(data2, session=session)
        # All operations commit or rollback together
```

## Security Best Practices

### 1. Authentication
- Always validate JWT tokens
- Use proper token expiration
- Implement token refresh mechanism

### 2. Input Validation
- Use Pydantic schemas for all inputs
- Validate file uploads
- Sanitize user inputs

### 3. Error Handling
- Don't expose sensitive information in errors
- Use generic error messages for security
- Log security events

## Performance Considerations

### 1. Database
- Use proper indexing
- Implement connection pooling
- Use pagination for large datasets

### 2. Caching
- Cache frequently accessed data
- Use Redis for distributed caching
- Implement cache invalidation

### 3. Async Operations
- Use async/await for I/O operations
- Implement proper error handling
- Use connection pooling

## Deployment

### 1. Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5555

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5555"]
```

### 2. Environment Variables
```bash
# Production environment
DATABASE_URL=mongodb://prod-server:27017
SECRET_KEY=super-secure-production-key
DEBUG=false
LOG_LEVEL=WARNING
```

### 3. Health Checks
- Implement health check endpoints
- Monitor database connectivity
- Track application metrics

## Troubleshooting

### Common Issues
1. **Import Errors**: Check PYTHONPATH and virtual environment
2. **Database Connection**: Verify MongoDB is running and accessible
3. **JWT Errors**: Check secret key and token expiration
4. **CORS Issues**: Verify allowed origins in configuration

### Debugging
```bash
# Enable debug mode
DEBUG=true python -m app.main

# Check logs
tail -f logs/app.log

# Database connection test
python -c "from app.database.connection import health_check; print(health_check())"
```

## Contributing

1. Follow the code conventions
2. Write tests for new features
3. Update documentation
4. Use meaningful commit messages
5. Create pull requests for review

---

*For more detailed information, see the specific documentation sections.*
