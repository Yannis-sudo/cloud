"""Admin interface for managing AI models."""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "mongodb://mongodb:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "copilot")


class ModelCatalog(BaseModel):
    """Model catalog document."""
    
    type: str
    models: list[str]


# MongoDB client
client = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global client
    # Startup
    client = AsyncIOMotorClient(DATABASE_URL)
    yield
    # Shutdown
    client.close()


# Create FastAPI app
app = FastAPI(
    title="AI Models Admin Interface",
    description="Admin interface for managing AI models",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type"],
)


class FreeModelsResponse(BaseModel):
    """Response schema for free models."""
    models: list[str]


class AddModelRequest(BaseModel):
    """Request schema for adding a model."""
    model_name: str = Field(..., description="Name of the AI model to add")
    
    model_config = {"protected_namespaces": ()}


async def get_catalog_collection():
    """Get the model catalog collection."""
    db = client[DATABASE_NAME]
    return db["model-catalog"]


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the admin interface HTML."""
    return FileResponse("static/index.html")


@app.get("/api/free-models", response_model=FreeModelsResponse)
async def get_free_models():
    """Get free AI models."""
    collection = await get_catalog_collection()
    catalog = await collection.find_one({"type": "free-models"})
    
    if not catalog:
        return FreeModelsResponse(models=[])
    
    return FreeModelsResponse(models=catalog.get("models", []))


@app.post("/api/free-models", response_model=FreeModelsResponse)
async def add_free_model(request: AddModelRequest):
    """Add a model to free models."""
    collection = await get_catalog_collection()
    catalog = await collection.find_one({"type": "free-models"})
    
    if not catalog:
        # Create new entry
        await collection.insert_one({"type": "free-models", "models": [request.model_name]})
        return FreeModelsResponse(models=[request.model_name])
    
    models = catalog.get("models", [])
    if request.model_name in models:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Model already exists")
    
    models.append(request.model_name)
    await collection.update_one(
        {"type": "free-models"},
        {"$set": {"models": models}}
    )
    
    return FreeModelsResponse(models=models)


@app.delete("/api/free-models/{model_name}", response_model=FreeModelsResponse)
async def remove_free_model(model_name: str):
    """Remove a model from free models."""
    collection = await get_catalog_collection()
    catalog = await collection.find_one({"type": "free-models"})
    
    if not catalog:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Free models catalog not found")
    
    models = catalog.get("models", [])
    if model_name not in models:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Model not found")
    
    models.remove(model_name)
    await collection.update_one(
        {"type": "free-models"},
        {"$set": {"models": models}}
    )
    
    return FreeModelsResponse(models=models)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=6769)
