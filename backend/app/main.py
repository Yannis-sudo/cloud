"""FastAPI application initialization."""

from app.routes.email import getemails, addemailserver, addfolder, getfolders
from app.routes.email.sendemail import router as send_email_router
from app.routes.notes import addnote, addlist, getlists, getnotes, deletelist, updatenotecolumn, updatepermissions, getpermissions
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
app.include_router(getemails.router, prefix="/api")
app.include_router(addemailserver.router, prefix="/api")
app.include_router(addfolder.router, prefix="/api")
app.include_router(getfolders.router, prefix="/api")
app.include_router(send_email_router, prefix="/api")
app.include_router(addnote.router, prefix="/api")
app.include_router(addlist.router, prefix="/api")
app.include_router(getlists.router, prefix="/api")
app.include_router(getnotes.router, prefix="/api")
app.include_router(deletelist.router, prefix="/api")
app.include_router(updatenotecolumn.router, prefix="/api")
app.include_router(updatepermissions.router, prefix="/api")
app.include_router(getpermissions.router, prefix="/api")

@app.get("/", tags=["health"])
async def root() -> dict[str, str]:
    """Health check endpoint.
    
    Returns:
        dict: API status message.
    """
    return {"message": "API is running"}