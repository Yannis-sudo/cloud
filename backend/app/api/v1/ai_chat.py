"""AI chat message API endpoints."""

import logging
from fastapi import APIRouter, Depends, HTTPException

from app.auth.dependencies import get_current_active_user
from app.auth.models import User
from app.schemas.ai_chat import ChatMessageRequest, ChatMessageResponse, AvailableModelsResponse
from app.modules.ai_chats.ai_chat_message import check_model_permission, get_user_available_models

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/available-models",
    response_model=AvailableModelsResponse,
    status_code=200,
    summary="Get available AI models",
    description="Get the list of AI models available for the current user"
)
async def get_available_models(
    current_user: User = Depends(get_current_active_user())
):
    """Get available AI models for the current user.
    
    Args:
        current_user: Currently authenticated active user
        
    Returns:
        AvailableModelsResponse: List of available model names
    """
    models = await get_user_available_models(str(current_user.id))
    # Convert ModelInfo objects to dictionaries for response serialization
    models_dict = [m.model_dump() for m in models]
    return AvailableModelsResponse(models=models_dict)
