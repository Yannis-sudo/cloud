"""FastAPI application initialization with new modular architecture."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database.connection import health_check, close_connection
from app.core.exceptions import BaseCustomException
from app.schemas.common import ErrorResponse

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
    
    # Check database health
    if not health_check():
        logger.error("Database health check failed on startup")
        raise Exception("Database connection failed")
    
    logger.info("Application startup completed")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
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
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
)


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
        content=ErrorResponse(
            success=False,
            message="Internal server error",
            error_code="INTERNAL_SERVER_ERROR"
        ).dict()
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
from app.api.v1 import auth, accounts, emails, notes, files, users, health

# API v1 endpoints
app.include_router(
    auth.router,
    prefix="/api/v1/auth",
    tags=["authentication"]
)

app.include_router(
    accounts.router,
    prefix="/api/v1/accounts",
    tags=["accounts"]
)

app.include_router(
    emails.router,
    prefix="/api/v1/emails",
    tags=["emails"]
)

app.include_router(
    notes.router,
    prefix="/api/v1/notes",
    tags=["notes"]
)

app.include_router(
    files.router,
    prefix="/api/v1/files",
    tags=["files"]
)

app.include_router(
    users.router,
    prefix="/api/v1/users",
    tags=["users"]
)

app.include_router(
    health.router,
    prefix="/api/v1",
    tags=["health"]
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