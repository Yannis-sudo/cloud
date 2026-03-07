"""FastAPI application initialization."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routes import login, createaccount

settings = get_settings()
app = FastAPI(
    title="Copilot API",
    description="Authentication and user management API",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Include routers
app.include_router(login.router, prefix="/api")
app.include_router(createaccount.router, prefix="/api")


@app.get("/", tags=["health"])
async def root() -> dict[str, str]:
    """Health check endpoint.
    
    Returns:
        dict: API status message.
    """
    return {"message": "API is running"}