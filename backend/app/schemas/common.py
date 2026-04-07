"""Common schemas for API responses and errors."""

from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Union, Generic, TypeVar
from datetime import datetime

T = TypeVar('T')


class BaseResponse(BaseModel, Generic[T]):
    """Base response model."""
    
    success: bool = Field(..., description="Whether the request was successful")
    message: str = Field(..., description="Response message")
    data: Optional[T] = Field(None, description="Response data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Operation completed successfully",
                "data": {},
                "timestamp": "2023-01-01T00:00:00Z"
            }
        }


class SuccessResponse(BaseResponse[Dict[str, Any]]):
    """Success response model."""
    
    success: bool = Field(default=True, description="Always true for success responses")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Operation completed successfully",
                "data": {},
                "timestamp": "2023-01-01T00:00:00Z"
            }
        }


class ErrorResponse(BaseModel):
    """Error response model."""
    
    success: bool = Field(default=False, description="Always false for error responses")
    message: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Application-specific error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "message": "Validation failed",
                "error_code": "VALIDATION_ERROR",
                "details": {
                    "field": "email",
                    "error": "Invalid email format"
                },
                "timestamp": "2023-01-01T00:00:00Z"
            }
        }


class ValidationErrorDetail(BaseModel):
    """Validation error detail model."""
    
    field: str = Field(..., description="Field name")
    message: str = Field(..., description="Error message")
    value: Optional[Any] = Field(None, description="Invalid value")
    
    class Config:
        json_schema_extra = {
            "example": {
                "field": "email",
                "message": "Invalid email format",
                "value": "invalid-email"
            }
        }


class ValidationErrorResponse(ErrorResponse):
    """Validation error response model."""
    
    error_code: str = Field(default="VALIDATION_ERROR", description="Error code")
    validation_errors: List[ValidationErrorDetail] = Field(..., description="List of validation errors")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
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
        }


class NotFoundResponse(ErrorResponse):
    """Not found error response model."""
    
    error_code: str = Field(default="NOT_FOUND", description="Error code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "message": "Resource not found",
                "error_code": "NOT_FOUND",
                "timestamp": "2023-01-01T00:00:00Z"
            }
        }


class UnauthorizedResponse(ErrorResponse):
    """Unauthorized error response model."""
    
    error_code: str = Field(default="UNAUTHORIZED", description="Error code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "message": "Authentication required",
                "error_code": "UNAUTHORIZED",
                "timestamp": "2023-01-01T00:00:00Z"
            }
        }


class ForbiddenResponse(ErrorResponse):
    """Forbidden error response model."""
    
    error_code: str = Field(default="FORBIDDEN", description="Error code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "message": "Access denied",
                "error_code": "FORBIDDEN",
                "timestamp": "2023-01-01T00:00:00Z"
            }
        }


class ConflictResponse(ErrorResponse):
    """Conflict error response model."""
    
    error_code: str = Field(default="CONFLICT", description="Error code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "message": "Resource already exists",
                "error_code": "CONFLICT",
                "timestamp": "2023-01-01T00:00:00Z"
            }
        }


class RateLimitResponse(ErrorResponse):
    """Rate limit error response model."""
    
    error_code: str = Field(default="RATE_LIMIT_EXCEEDED", description="Error code")
    retry_after: Optional[int] = Field(None, description="Seconds to wait before retrying")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "message": "Rate limit exceeded",
                "error_code": "RATE_LIMIT_EXCEEDED",
                "retry_after": 3600,
                "timestamp": "2023-01-01T00:00:00Z"
            }
        }


class PaginatedResponse(BaseResponse[Dict[str, Any]]):
    """Paginated response model."""
    
    pagination: Dict[str, Any] = Field(..., description="Pagination information")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Data retrieved successfully",
                "data": [],
                "pagination": {
                    "page": 1,
                    "limit": 20,
                    "total": 100,
                    "pages": 5,
                    "has_next": True,
                    "has_prev": False
                },
                "timestamp": "2023-01-01T00:00:00Z"
            }
        }


class HealthCheckResponse(BaseModel):
    """Health check response model."""
    
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")
    services: Dict[str, str] = Field(..., description="Service health status")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "timestamp": "2023-01-01T00:00:00Z",
                "services": {
                    "database": "healthy",
                    "email_service": "healthy",
                    "file_storage": "healthy"
                }
            }
        }
