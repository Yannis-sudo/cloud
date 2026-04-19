"""JWT authentication backend for FastAPI Users."""

from fastapi_users.authentication import JWTStrategy, AuthenticationBackend, BearerTransport
from app.config import get_settings

settings = get_settings()


def get_jwt_strategy() -> JWTStrategy:
    """Get JWT strategy for FastAPI Users.
    
    Returns:
        JWTStrategy: JWT authentication strategy
    """
    return JWTStrategy(
        secret=settings.JWT_SECRET,
        lifetime_seconds=settings.JWT_EXPIRATION_SECONDS,
        algorithm=settings.JWT_ALGORITHM,
    )


def get_bearer_transport() -> BearerTransport:
    """Get Bearer token transport.
    
    Returns:
        BearerTransport: Bearer transport for JWT tokens
    """
    return BearerTransport(tokenUrl="auth/jwt/login")


# Create the authentication backend
jwt_authentication = AuthenticationBackend(
    name="jwt",
    transport=get_bearer_transport(),
    get_strategy=get_jwt_strategy,
)
