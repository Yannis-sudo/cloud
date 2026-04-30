"""AI chat message API endpoints."""

import logging
from fastapi import APIRouter, Depends, HTTPException

from app.auth.dependencies import get_current_active_user
from app.auth.models import User
from app.schemas.ai_chat import (
    ChatMessageRequest, ChatMessageResponse, AvailableModelsResponse,
    CreateChatRequest, CreateChatResponse, SendMessageRequest, GetChatsResponse
)
from app.modules.ai_chats.ai_chat_message import check_model_permission, get_user_available_models
from app.modules.ai_chats.chat_operations import create_chat, send_message, get_user_chats

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


@router.post(
    "/create-chat",
    response_model=CreateChatResponse,
    status_code=201,
    summary="Create a new chat",
    description="Create a new AI chat for the current user"
)
async def create_new_chat(
    request: CreateChatRequest,
    current_user: User = Depends(get_current_active_user())
):
    """Create a new AI chat for the current user.
    
    Args:
        request: Empty request body
        current_user: Currently authenticated active user
        
    Returns:
        CreateChatResponse: The created chat's ID and title
    """
    try:
        chat_id = await create_chat(str(current_user.id))
        return CreateChatResponse(chat_id=chat_id, title="New Chat")
    except Exception as e:
        logger.error("Error creating chat for user %s: %s", current_user.id, e)
        raise HTTPException(status_code=500, detail="Failed to create chat")


@router.post(
    "/send-message",
    response_model=ChatMessageResponse,
    status_code=200,
    summary="Send a message to a chat",
    description="Send a message to an AI chat and get the AI response"
)
async def send_chat_message(
    request: SendMessageRequest,
    current_user: User = Depends(get_current_active_user())
):
    """Send a message to an AI chat and get the AI response.
    
    Args:
        request: Message request with chat_id, model_name, and message
        current_user: Currently authenticated active user
        
    Returns:
        ChatMessageResponse: The AI's response
        
    Raises:
        HTTPException 403: If user doesn't have permission to use the model
        HTTPException 404: If chat is not found
        HTTPException 400: If chat doesn't belong to user
    """
    try:
        ai_response = await send_message(
            str(current_user.id),
            request.chat_id,
            request.message,
            request.model_name
        )
        return ChatMessageResponse(model_name=request.model_name, text=ai_response)
    except PermissionError as e:
        logger.warning("Permission denied for user %s: %s", current_user.id, e)
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        logger.warning("Invalid request for user %s: %s", current_user.id, e)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Error sending message for user %s: %s", current_user.id, e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/chats",
    response_model=GetChatsResponse,
    status_code=200,
    summary="Get user's chats",
    description="Get all AI chats for the current user"
)
async def get_user_chat_list(
    current_user: User = Depends(get_current_active_user())
):
    """Get all AI chats for the current user.
    
    Args:
        current_user: Currently authenticated active user
        
    Returns:
        GetChatsResponse: List of user's chats with messages
    """
    try:
        chats = await get_user_chats(str(current_user.id))
        return GetChatsResponse(chats=chats)
    except Exception as e:
        logger.error("Error getting chats for user %s: %s", current_user.id, e)
        raise HTTPException(status_code=500, detail="Failed to retrieve chats")
