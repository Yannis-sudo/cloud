"""Model admin API endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.modules.ai_chats.models import ModelCatalog

router = APIRouter()


class FreeModelsResponse(BaseModel):
    """Response schema for free models."""
    
    models: list[str] = Field(..., description="List of free AI model names")


class AddModelRequest(BaseModel):
    """Request schema for adding a model."""
    
    model_name: str = Field(..., description="Name of the AI model to add")


@router.get(
    "/model-catalog/free-models",
    response_model=FreeModelsResponse,
    status_code=200,
    summary="Get free models",
    description="Get the list of free AI models"
)
async def get_free_models():
    """Get free AI models.
    
    Returns:
        FreeModelsResponse: List of free model names
    """
    catalog = await ModelCatalog.find_one(ModelCatalog.type == "free-models")
    
    if not catalog:
        # Create empty free-models entry if it doesn't exist
        catalog = ModelCatalog(type="free-models", models=[])
        await catalog.insert()
    
    return FreeModelsResponse(models=catalog.models)


@router.post(
    "/model-catalog/free-models",
    response_model=FreeModelsResponse,
    status_code=200,
    summary="Add free model",
    description="Add a model to the free models list"
)
async def add_free_model(request: AddModelRequest):
    """Add a model to free models.
    
    Args:
        request: Add model request with model name
        
    Returns:
        FreeModelsResponse: Updated list of free model names
    """
    catalog = await ModelCatalog.find_one(ModelCatalog.type == "free-models")
    
    if not catalog:
        # Create free-models entry if it doesn't exist
        catalog = ModelCatalog(type="free-models", models=[])
        await catalog.insert()
    
    if request.model_name in catalog.models:
        raise HTTPException(
            status_code=400,
            detail="Model already exists in free models"
        )
    
    catalog.models.append(request.model_name)
    await catalog.save()
    
    return FreeModelsResponse(models=catalog.models)


@router.delete(
    "/model-catalog/free-models/{model_name}",
    response_model=FreeModelsResponse,
    status_code=200,
    summary="Remove free model",
    description="Remove a model from the free models list"
)
async def remove_free_model(model_name: str):
    """Remove a model from free models.
    
    Args:
        model_name: Name of the model to remove
        
    Returns:
        FreeModelsResponse: Updated list of free model names
    """
    catalog = await ModelCatalog.find_one(ModelCatalog.type == "free-models")
    
    if not catalog:
        raise HTTPException(
            status_code=404,
            detail="Free models catalog not found"
        )
    
    if model_name not in catalog.models:
        raise HTTPException(
            status_code=404,
            detail="Model not found in free models"
        )
    
    catalog.models.remove(model_name)
    await catalog.save()
    
    return FreeModelsResponse(models=catalog.models)
