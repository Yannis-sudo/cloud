"""Model admin API endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.modules.ai_chats.models import ModelCatalog, ModelInfo

router = APIRouter()


class FreeModelsResponse(BaseModel):
    """Response schema for free models."""
    
    models: list[ModelInfo] = Field(..., description="List of free AI model info")


class AddModelRequest(BaseModel):
    """Request schema for adding a model."""
    
    name: str = Field(..., description="Name/ID of the AI model")
    alias: str = Field(..., description="Display alias for the model")
    description: str = Field(default="", description="Model description")


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
        FreeModelsResponse: List of free model info
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
        request: Add model request with model name, alias, and description
        
    Returns:
        FreeModelsResponse: Updated list of free model info
    """
    catalog = await ModelCatalog.find_one(ModelCatalog.type == "free-models")
    
    if not catalog:
        # Create free-models entry if it doesn't exist
        catalog = ModelCatalog(type="free-models", models=[])
        await catalog.insert()
    
    # Check if model name already exists
    for model in catalog.models:
        if model.name == request.name:
            raise HTTPException(
                status_code=400,
                detail="Model already exists in free models"
            )
    
    new_model = ModelInfo(name=request.name, alias=request.alias, description=request.description)
    catalog.models.append(new_model)
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
        FreeModelsResponse: Updated list of free model info
    """
    catalog = await ModelCatalog.find_one(ModelCatalog.type == "free-models")
    
    if not catalog:
        raise HTTPException(
            status_code=404,
            detail="Free models catalog not found"
        )
    
    # Find and remove the model by name
    found = False
    updated_models = []
    for model in catalog.models:
        if model.name == model_name:
            found = True
        else:
            updated_models.append(model)
    
    if not found:
        raise HTTPException(
            status_code=404,
            detail="Model not found in free models"
        )
    
    catalog.models = updated_models
    await catalog.save()
    
    return FreeModelsResponse(models=catalog.models)
