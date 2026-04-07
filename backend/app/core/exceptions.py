"""Custom exceptions for the application."""

from typing import Optional, Any, Dict


class BaseCustomException(Exception):
    """Base exception for all custom exceptions."""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(BaseCustomException):
    """Authentication related errors."""
    
    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=401, details=details)


class AuthorizationError(BaseCustomException):
    """Authorization related errors."""
    
    def __init__(self, message: str = "Access denied", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=403, details=details)


class ValidationError(BaseCustomException):
    """Validation errors."""
    
    def __init__(self, message: str = "Validation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=422, details=details)


class NotFoundError(BaseCustomException):
    """Resource not found errors."""
    
    def __init__(self, message: str = "Resource not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=404, details=details)


class ConflictError(BaseCustomException):
    """Resource conflict errors."""
    
    def __init__(self, message: str = "Resource conflict", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=409, details=details)


class DatabaseError(BaseCustomException):
    """Database operation errors."""
    
    def __init__(self, message: str = "Database operation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=500, details=details)


class EmailError(BaseCustomException):
    """Email operation errors."""
    
    def __init__(self, message: str = "Email operation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=500, details=details)


class FileError(BaseCustomException):
    """File operation errors."""
    
    def __init__(self, message: str = "File operation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=500, details=details)


class RateLimitError(BaseCustomException):
    """Rate limiting errors."""
    
    def __init__(self, message: str = "Rate limit exceeded", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=429, details=details)


class ExternalServiceError(BaseCustomException):
    """External service errors (IMAP, SMTP, etc.)."""
    
    def __init__(self, message: str = "External service error", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=502, details=details)
