"""Authentication API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer

from app.core.auth import AuthService
from app.core.security import TokenData
from app.core.exceptions import (
    AuthenticationError, ValidationError, NotFoundError,
    ConflictError
)
from app.schemas.auth import (
    LoginRequest, RegisterRequest, TokenResponse,
    RefreshTokenRequest, PasswordResetRequest,
    PasswordResetConfirmRequest, ChangePasswordRequest,
    LoginResponse, LogoutResponse
)
from app.schemas.common import (
    SuccessResponse, ErrorResponse, ValidationErrorResponse,
    NotFoundResponse, ConflictResponse
)
from app.dependencies import get_current_user

router = APIRouter()
security = HTTPBearer()
auth_service = AuthService()


def handle_auth_error(error: Exception):
    """Handle authentication errors and convert to HTTP exceptions."""
    if isinstance(error, AuthenticationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif isinstance(error, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error)
        )
    elif isinstance(error, NotFoundError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )
    elif isinstance(error, ConflictError):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate user",
    description="Authenticate a user with email and password and return JWT tokens"
)
async def login(request: LoginRequest) -> LoginResponse:
    """Authenticate a user and return tokens."""
    try:
        result = await auth_service.login(request.email, request.password)
        
        return LoginResponse(
            message="Login successful",
            user=result["user"],
            tokens=result["tokens"]
        )
    except Exception as e:
        handle_auth_error(e)


@router.post(
    "/register",
    response_model=LoginResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Register a new user and return JWT tokens"
)
async def register(request: RegisterRequest) -> LoginResponse:
    """Register a new user and return tokens."""
    try:
        result = await auth_service.register(
            username=request.username,
            email=request.email,
            password=request.password,
            first_name=request.first_name,
            last_name=request.last_name
        )
        
        return LoginResponse(
            message="Registration successful",
            user=result["user"],
            tokens=result["tokens"]
        )
    except Exception as e:
        handle_auth_error(e)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description="Refresh access token using a valid refresh token"
)
async def refresh_token(request: RefreshTokenRequest) -> TokenResponse:
    """Refresh access token."""
    try:
        tokens = await auth_service.refresh_token(request.refresh_token)
        
        return TokenResponse(**tokens)
    except Exception as e:
        handle_auth_error(e)


@router.post(
    "/logout",
    response_model=LogoutResponse,
    status_code=status.HTTP_200_OK,
    summary="Logout user",
    description="Logout user by invalidating refresh token"
)
async def logout(request: RefreshTokenRequest) -> LogoutResponse:
    """Logout user."""
    try:
        await auth_service.logout(request.refresh_token)
        
        return LogoutResponse(message="Logout successful")
    except Exception as e:
        handle_auth_error(e)


@router.post(
    "/password-reset-request",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Request password reset",
    description="Request a password reset token via email"
)
async def request_password_reset(request: PasswordResetRequest) -> SuccessResponse:
    """Request password reset."""
    try:
        await auth_service.request_password_reset(request.email)
        
        return SuccessResponse(
            message="If the email exists, a password reset link has been sent"
        )
    except Exception as e:
        handle_auth_error(e)


@router.post(
    "/password-reset-confirm",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Confirm password reset",
    description="Reset password using a valid reset token"
)
async def confirm_password_reset(request: PasswordResetConfirmRequest) -> SuccessResponse:
    """Confirm password reset."""
    try:
        await auth_service.reset_password(request.token, request.new_password)
        
        return SuccessResponse(message="Password reset successful")
    except Exception as e:
        handle_auth_error(e)


@router.post(
    "/change-password",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Change password",
    description="Change user password (requires authentication)"
)
async def change_password(
    request: ChangePasswordRequest,
    current_user: TokenData = Depends(get_current_user)
) -> SuccessResponse:
    """Change user password."""
    try:
        await auth_service.change_password(
            user_id=current_user.user_id,
            current_password=request.current_password,
            new_password=request.new_password
        )
        
        return SuccessResponse(message="Password changed successfully")
    except Exception as e:
        handle_auth_error(e)


@router.get(
    "/me",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user",
    description="Get current authenticated user information"
)
async def get_current_user_info(
    current_user: TokenData = Depends(get_current_user)
) -> SuccessResponse:
    """Get current user information."""
    try:
        user = await auth_service.verify_token(current_user.email)
        
        if not user:
            raise AuthenticationError("User not found")
        
        return SuccessResponse(
            message="User information retrieved successfully",
            data=user
        )
    except Exception as e:
        handle_auth_error(e)
