"""AI chat message API endpoints."""

from fastapi import APIRouter, Depends, HTTPException

from app.auth.dependencies import get_current_active_user
from app.auth.models import User
from app.schemas.ai_chat import ChatMessageRequest, ChatMessageResponse, AvailableModelsResponse
from app.modules.ai_chats.ai_chat_message import check_model_permission, get_user_available_models

router = APIRouter()


@router.post(
    "/ai-chat-message",
    response_model=ChatMessageResponse,
    status_code=200,
    summary="Send message to AI model",
    description="Send a message to an AI model and receive a response"
)
async def ai_chat_message(
    request: ChatMessageRequest,
    current_user: User = Depends(get_current_active_user)
):
    """AI chat message endpoint.
    
    Args:
        request: Chat message request with model name and message
        current_user: Currently authenticated active user
        
    Returns:
        ChatMessageResponse: Response with model name and generated text
    """
    # Check if user is allowed to use this model
    has_permission = await check_model_permission(str(current_user.id), request.model_name)
    
    if not has_permission:
        raise HTTPException(
            status_code=403,
            detail="User not authorized to use this model"
        )
    
    # TODO: Integrate with ai_chat_message module for actual AI processing
    # For now, return a placeholder response
    return ChatMessageResponse(
        model_name=request.model_name,
        text="Placeholder response - module integration pending"
    )


@router.get(
    "/available-models",
    response_model=AvailableModelsResponse,
    status_code=200,
    summary="Get available AI models",
    description="Get the list of AI models available for the current user"
)
async def get_available_models(
    current_user: User = Depends(get_current_active_user)
):
    """Get available AI models for the current user.
    
    Args:
        current_user: Currently authenticated active user
        
    Returns:
        AvailableModelsResponse: List of available model names
    """
    models = await get_user_available_models(str(current_user.id))
    return AvailableModelsResponse(models=models)
