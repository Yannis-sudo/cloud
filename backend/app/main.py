"""FastAPI application initialization with new modular architecture."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database.connection import health_check, close_connection
from app.database.async_db import init_db, close_db
from app.core.exceptions import BaseCustomException
from app.schemas.common import ErrorResponse
from app.auth.models import User
from app.modules.ai_chats.models import UserAIModels, ModelCatalog

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting up application...")
    
    try:
        # Initialize Beanie with User model for FastAPI Users and AI models
        await init_db([User, UserAIModels, ModelCatalog])
        logger.info("Beanie database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Beanie: {e}")
        raise Exception(f"Database initialization failed: {e}")
    
    logger.info("Application startup completed")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    await close_db()
    close_connection()
    logger.info("Application shutdown completed")


# Create FastAPI app
app = FastAPI(
    title="Cloud API",
    description="A modern, modular backend API for cloud services",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.allow_all_origins else settings.CORS_ORIGINS,
    allow_credentials=not settings.allow_all_origins,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
)


# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests and responses for debugging."""
    logger.info(f"Incoming request: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response


# Exception handlers
@app.exception_handler(BaseCustomException)
async def custom_exception_handler(request: Request, exc: BaseCustomException):
    """Handle custom exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            success=False,
            message=exc.message,
            error_code=exc.__class__.__name__,
            details=exc.details
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "error_code": "INTERNAL_SERVER_ERROR"
        }
    )


# Health check endpoint
@app.get(
    "/health",
    tags=["health"],
    summary="Health check",
    description="Check the health of the application and its dependencies"
)
async def health_check_endpoint():
    """Health check endpoint."""
    try:
        # Check database
        db_healthy = health_check()
        
        services = {
            "database": "healthy" if db_healthy else "unhealthy",
            "api": "healthy"
        }
        
        overall_status = "healthy" if all(status == "healthy" for status in services.values()) else "unhealthy"
        
        return {
            "status": overall_status,
            "version": "1.0.0",
            "services": services,
            "timestamp": "2023-01-01T00:00:00Z"  # Will be updated automatically
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "version": "1.0.0",
                "services": {"database": "unhealthy", "api": "healthy"},
                "error": str(e)
            }
        )


# Include API routers
from app.api.v1 import health
from app.api.v1 import ai_chat
from app.api.v1 import model_admin
from app.auth.routes import get_auth_router

# FastAPI Users authentication routers (replaces old auth router)
auth_router = get_auth_router()
app.include_router(
    auth_router,
    prefix="/api/v1/auth",
    tags=["authentication"]
)

app.include_router(
    health.router,
    prefix="/api/v1",
    tags=["health"]
)

app.include_router(
    ai_chat.router,
    prefix="/api/v1",
    tags=["ai-chat"]
)

app.include_router(
    model_admin.router,
    prefix="/api/v1",
    tags=["model-admin"]
)


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint."""
    return {
        "message": "Cloud API is running",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=5555,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )