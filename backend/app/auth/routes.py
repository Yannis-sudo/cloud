"""Authentication routes with FastAPI Users integration."""

from fastapi import APIRouter, Depends
from fastapi_users import FastAPIUsers
from beanie import PydanticObjectId

from app.auth.backend import jwt_authentication
from app.auth.database import get_user_db
from app.auth.manager import UserManager, get_user_manager
from app.auth.models import User
from app.auth.schemas import UserRead, UserCreate, UserUpdate
from app.auth.dependencies import set_fastapi_users


# Initialize FastAPI Users
fastapi_users = FastAPIUsers[User, PydanticObjectId](
    get_user_manager,
    [jwt_authentication],
)

# Store reference in dependencies for use in other modules
set_fastapi_users(fastapi_users)


def get_auth_router() -> APIRouter:
    """Create and return the authentication router.
    
    Returns:
        APIRouter: Router with all auth endpoints mounted
    """
    router = APIRouter()
    
    # Mount FastAPI Users routers
    
    # JWT authentication routers (login/logout)
    router.include_router(
        fastapi_users.get_auth_router(jwt_authentication),
        prefix="/jwt",
        tags=["authentication"],
    )
    
    # User registration router
    router.include_router(
        fastapi_users.get_register_router(UserRead, UserCreate),
        tags=["authentication"],
    )
    
    # Optional: Email verification router (only if enabled)
    router.include_router(
        fastapi_users.get_verify_router(UserRead),
        tags=["authentication"],
    )
    
    # Password reset routers (forgot password, reset password)
    router.include_router(
        fastapi_users.get_reset_password_router(),
        tags=["authentication"],
    )
    
    # User management routers
    router.include_router(
        fastapi_users.get_users_router(UserRead, UserUpdate),
        prefix="/users",
        tags=["users"],
    )
    
    return router
