# AI Agent Documentation

This documentation provides comprehensive context for AI agents to understand the codebase structure, patterns, and conventions for consistent contributions.

## Codebase Context

### Project Overview
The Cloud Backend API is a modern, modular FastAPI application that provides:
- JWT-based authentication with refresh tokens
- Email management via IMAP/SMTP
- Notes management with permissions
- File storage using MongoDB GridFS
- User management and profiles

### Architecture Philosophy
- **Clean Architecture**: Clear separation between API, business logic, and data access
- **Domain-Driven Design**: Modules organized by business domains
- **Repository Pattern**: Abstract data access with MongoDB
- **Dependency Injection**: FastAPI's DI for testability and modularity
- **Type Safety**: Full type hints throughout the codebase

## Module Structure

### Core Components

#### 1. Database Layer (`app/database/`)
```python
# Base repository pattern
class BaseRepository(Generic[T]):
    async def create(self, document: Dict[str, Any]) -> str
    async def get_by_id(self, document_id: str) -> Optional[Dict[str, Any]]
    async def get_many(self, query: Dict[str, Any]) -> List[Dict[str, Any]]
    async def update(self, document_id: str, update_data: Dict[str, Any]) -> bool
    async def delete(self, document_id: str) -> bool
```

**Key Patterns:**
- All repositories inherit from `BaseRepository`
- Use `ObjectId` for MongoDB IDs
- Include timestamps (`created_at`, `updated_at`)
- Serialize documents for API responses (convert ObjectId to string)

#### 2. Service Layer (`app/modules/*/service.py`)
```python
class FeatureService:
    def __init__(self):
        self.repository = FeatureRepository()
    
    async def business_method(self, params) -> ResultType:
        # Validate input
        self._validate_input(params)
        
        # Business logic
        result = await self.repository.operation(params)
        
        # Post-processing
        return self._process_result(result)
```

**Key Patterns:**
- Services contain business logic, not data access
- Use repositories for data operations
- Validate inputs and handle business rules
- Remove sensitive data (passwords) before returning

#### 3. API Layer (`app/api/v1/*.py`)
```python
@router.post("/endpoint", response_model=ResponseModel)
async def endpoint(
    request: RequestModel,
    current_user: TokenData = Depends(get_current_user),
    service: FeatureService = Depends(get_feature_service)
) -> ResponseModel:
    try:
        result = await service.method(**request.dict())
        return ResponseModel(**result)
    except CustomException as e:
        handle_custom_error(e)
```

**Key Patterns:**
- Thin controllers - only HTTP concerns
- Use dependency injection for services
- Standardized error handling with custom exceptions
- Response models for consistent API contracts

## Coding Patterns

### 1. Error Handling
```python
# Custom exceptions
from app.core.exceptions import ValidationError, NotFoundError, ConflictError

# Always use custom exceptions for business logic
if not email:
    raise ValidationError("Email is required")

if not user:
    raise NotFoundError("User not found")

if user_exists:
    raise ConflictError("User already exists")
```

### 2. Authentication Patterns
```python
# Protected endpoints
@router.get("/protected")
async def protected_endpoint(
    current_user: TokenData = Depends(get_current_user)
):
    # current_user.email and current_user.user_id are available
    pass

# Service-level authentication
async def get_user_data(user_id: str, requester_email: str):
    user = await self.repository.get_by_id(user_id)
    
    # Authorization check
    if user["email"] != requester_email:
        raise AuthorizationError("Access denied")
    
    return user
```

### 3. Database Patterns
```python
# Transaction usage
from app.database.connection import get_transaction

async def complex_operation():
    async with get_transaction() as session:
        # Multiple operations
        await repo1.create(data1, session=session)
        await repo2.update(data2, session=session)
        # Auto commit/rollback

# Query patterns
async def get_active_users():
    return await self.repository.get_many({
        "is_active": True,
        "created_at": {"$gte": datetime.utcnow() - timedelta(days=30)}
    })
```

### 4. Validation Patterns
```python
# Pydantic schemas for validation
class CreateUserRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=6)

# Service-level validation
def _validate_user_data(self, username: str, email: str, password: str):
    errors = []
    
    if not username or len(username) < 1:
        errors.append("Username is required")
    
    if "@" not in email:
        errors.append("Valid email is required")
    
    if len(password) < 6:
        errors.append("Password must be at least 6 characters")
    
    if errors:
        raise ValidationError("Validation failed", details={"errors": errors})
```

## Security Implementation

### 1. Password Security
```python
from app.core.security import get_password_hash, verify_password

# Hash passwords
hashed_password = get_password_hash(plain_password)

# Verify passwords
is_valid = verify_password(plain_password, hashed_password)
```

### 2. JWT Tokens
```python
from app.core.security import create_access_token, verify_token

# Create tokens
access_token = create_access_token(
    data={"sub": user["email"], "user_id": user["_id"]}
)

# Verify tokens
token_data = verify_token(token)
if token_data:
    user_email = token_data.email
    user_id = token_data.user_id
```

### 3. Input Sanitization
```python
# Always validate and sanitize inputs
def sanitize_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
    sanitized = {}
    
    for key, value in data.items():
        if isinstance(value, str):
            sanitized[key] = value.strip()
        else:
            sanitized[key] = value
    
    return sanitized
```

## Data Flow Patterns

### 1. Request Flow
```
HTTP Request -> API Endpoint -> Service -> Repository -> Database
                |              |           |            |
                v              v           v            v
            Validation    Business    Data Access  MongoDB
            Response      Logic       Layer        Storage
```

### 2. Authentication Flow
```
Request -> JWT Validation -> TokenData -> Service Authorization -> Business Logic
```

### 3. Error Flow
```
Business Error -> Custom Exception -> HTTP Exception Handler -> Standardized Error Response
```

## File Organization Patterns

### 1. Module Structure
```
modules/feature/
|-- __init__.py
|-- service.py      # Business logic
|-- models.py       # Data models
|-- validators.py   # Input validation
`-- utils.py        # Module-specific utilities
```

### 2. Repository Structure
```
database/repositories/
|-- base.py         # Base repository
|-- users.py        # User operations
|-- emails.py       # Email operations
|-- notes.py        # Notes operations
`-- files.py        # File operations
```

### 3. API Structure
```
api/v1/
|-- auth.py         # Authentication endpoints
|-- accounts.py     # Account endpoints
|-- emails.py       # Email endpoints
|-- notes.py        # Notes endpoints
|-- files.py        # File endpoints
`-- users.py        # User endpoints
```

## Testing Patterns

### 1. Unit Tests
```python
@pytest.mark.asyncio
async def test_service_method():
    service = FeatureService()
    
    # Mock repository
    with patch.object(service.repository, 'create') as mock_create:
        mock_create.return_value = "test_id"
        
        result = await service.create_method(valid_data)
        
        assert result["id"] == "test_id"
        mock_create.assert_called_once_with(valid_data)
```

### 2. Integration Tests
```python
def test_api_endpoint():
    client = TestClient(app)
    
    response = client.post("/api/v1/endpoint", json=request_data)
    
    assert response.status_code == 200
    assert response.json()["success"] is True
```

## Performance Patterns

### 1. Database Optimization
```python
# Use indexes
await self.repository.create_index([("email", 1)], unique=True)

# Efficient queries
async def get_recent_users():
    return await self.repository.get_many(
        query={"created_at": {"$gte": datetime.utcnow() - timedelta(days=7)}},
        sort=[("created_at", -1)],
        limit=100
    )
```

### 2. Caching Patterns
```python
# Simple in-memory cache (for development)
from functools import lru_cache

@lru_cache(maxsize=128)
def get_cached_data(key: str):
    return expensive_operation(key)

# Redis cache (for production)
async def get_cached_user(user_id: str):
    cached = await redis.get(f"user:{user_id}")
    if cached:
        return json.loads(cached)
    
    user = await repository.get_by_id(user_id)
    await redis.setex(f"user:{user_id}", 3600, json.dumps(user))
    return user
```

## Common Gotchas

### 1. MongoDB ObjectId
```python
# WRONG: Treating ObjectId as string
user = await repository.get_by_id("507f1f77bcf86cd799439011")

# RIGHT: Convert to ObjectId
from bson import ObjectId
object_id = ObjectId("507f1f77bcf86cd799439011")
user = await repository.get_by_id(object_id)
```

### 2. Async/Await
```python
# WRONG: Forgetting await
result = repository.get_by_id(user_id)

# RIGHT: Using await
result = await repository.get_by_id(user_id)
```

### 3. Password Handling
```python
# WRONG: Storing plaintext passwords
user_data["password"] = password

# RIGHT: Hashing passwords
from app.core.security import get_password_hash
user_data["password"] = get_password_hash(password)
```

### 4. Error Exposure
```python
# WRONG: Exposing internal errors
except Exception as e:
    return {"error": str(e)}  # Might expose sensitive info

# RIGHT: Using custom exceptions
except Exception as e:
    logger.error(f"Internal error: {e}")
    raise DatabaseError("Operation failed")
```

## Best Practices Summary

1. **Always use type hints** for function signatures and variables
2. **Use custom exceptions** for business logic errors
3. **Never store plaintext passwords** - always hash them
4. **Validate all inputs** using Pydantic schemas
5. **Use dependency injection** for services and repositories
6. **Handle errors consistently** with standardized responses
7. **Write tests** for all business logic
8. **Use transactions** for multi-step operations
9. **Remove sensitive data** before returning responses
10. **Follow the established patterns** for consistency

## When Adding New Features

1. **Create repository** inheriting from `BaseRepository`
2. **Create service** with business logic and validation
3. **Create schemas** for request/response models
4. **Create API endpoints** with proper error handling
5. **Add authentication** if needed
6. **Write tests** for the new functionality
7. **Update documentation** with new endpoints

---

This documentation should be updated as the codebase evolves. Always follow the established patterns for consistency.
