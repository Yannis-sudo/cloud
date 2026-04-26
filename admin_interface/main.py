"""Admin interface for managing AI models."""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


class ModelInfo(BaseModel):
    """Model information with alias and description."""
    name: str = Field(..., description="Model name/ID")
    alias: str = Field(..., description="Display alias for the model")
    description: str = Field(default="", description="Model description")
    
    model_config = {"protected_namespaces": ()}


class FreeModelsResponse(BaseModel):
    """Response schema for free models."""
    models: list[ModelInfo]


class AddModelRequest(BaseModel):
    """Request schema for adding a model."""
    name: str = Field(..., description="Model name/ID")
    alias: str = Field(..., description="Display alias for the model")
    description: str = Field(default="", description="Model description")
    
    model_config = {"protected_namespaces": ()}


async def get_catalog_collection():
    """Get the model catalog collection."""
    db = client[DATABASE_NAME]
    return db["model-catalog"]


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the admin interface HTML."""
    from fastapi.responses import FileResponse
    return FileResponse("static/index.html")


@app.get("/api/free-models", response_model=FreeModelsResponse)
async def get_free_models():
    """Get free AI models."""
    collection = await get_catalog_collection()
    catalog = await collection.find_one({"type": "free-models"})
    
    if not catalog:
        logger.info("[DEBUG] No free-models entry found in catalog")
        return FreeModelsResponse(models=[])
    
    models_data = catalog.get("models", [])
    # Convert to ModelInfo objects
    models = [ModelInfo(**m) if isinstance(m, dict) else ModelInfo(name=m, alias=m, description="") for m in models_data]
    logger.info(f"[DEBUG] Free models from catalog: {models}")
    return FreeModelsResponse(models=models)


@app.post("/api/free-models", response_model=FreeModelsResponse)
async def add_free_model(request: AddModelRequest):
    """Add a model to free models."""
    logger.info(f"[DEBUG] Adding model to free models: {request.name}")
    collection = await get_catalog_collection()
    catalog = await collection.find_one({"type": "free-models"})
    
    new_model = ModelInfo(name=request.name, alias=request.alias, description=request.description)
    
    if not catalog:
        # Create new entry
        await collection.insert_one({"type": "free-models", "models": [new_model.dict()]})
        logger.info(f"[DEBUG] Created new free-models entry with: {new_model}")
        return FreeModelsResponse(models=[new_model])
    
    models_data = catalog.get("models", [])
    # Check if model name already exists
    for m in models_data:
        if isinstance(m, dict):
            if m.get("name") == request.name:
                from fastapi import HTTPException
                logger.warning(f"[DEBUG] Model {request.name} already exists in free models")
                raise HTTPException(status_code=400, detail="Model already exists")
        elif m == request.name:
            from fastapi import HTTPException
            logger.warning(f"[DEBUG] Model {request.name} already exists in free models")
            raise HTTPException(status_code=400, detail="Model already exists")
    
    models_data.append(new_model.dict())
    await collection.update_one(
        {"type": "free-models"},
        {"$set": {"models": models_data}}
    )
    models = [ModelInfo(**m) if isinstance(m, dict) else ModelInfo(name=m, alias=m, description="") for m in models_data]
    logger.info(f"[DEBUG] Added model {request.name} to free models. New list: {models}")
    return FreeModelsResponse(models=models)


@app.delete("/api/free-models/{model_name}", response_model=FreeModelsResponse)
async def remove_free_model(model_name: str):
    """Remove a model from free models."""
    logger.info(f"[DEBUG] Removing model from free models: {model_name}")
    collection = await get_catalog_collection()
    catalog = await collection.find_one({"type": "free-models"})
    
    if not catalog:
        from fastapi import HTTPException
        logger.warning("[DEBUG] Free models catalog not found")
        raise HTTPException(status_code=404, detail="Free models catalog not found")
    
    models_data = catalog.get("models", [])
    found = False
    updated_models = []
    
    for m in models_data:
        if isinstance(m, dict):
            if m.get("name") == model_name:
                found = True
            else:
                updated_models.append(m)
        elif m == model_name:
            found = True
        else:
            updated_models.append(m)
    
    if not found:
        from fastapi import HTTPException
        logger.warning(f"[DEBUG] Model {model_name} not found in free models")
        raise HTTPException(status_code=404, detail="Model not found")
    
    await collection.update_one(
        {"type": "free-models"},
        {"$set": {"models": updated_models}}
    )
    models = [ModelInfo(**m) if isinstance(m, dict) else ModelInfo(name=m, alias=m, description="") for m in updated_models]
    logger.info(f"[DEBUG] Removed model {model_name} from free models. New list: {models}")
    return FreeModelsResponse(models=models)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=6769)
