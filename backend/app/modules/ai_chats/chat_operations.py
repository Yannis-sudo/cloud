"""AI chat operations module."""

import logging
from beanie import PydanticObjectId
from datetime import datetime
from app.modules.ai_chats.models import AIChat, ChatMessage
from app.modules.ai_chats.ai_chat_message import check_model_permission

logger = logging.getLogger(__name__)


async def generate_chat_title() -> str:
    """Generate a chat title based on the conversation.
    
    This is a placeholder function that will be implemented later
    to generate meaningful titles from chat content.
    
    Returns:
        str: Generated chat title
    """
    # TODO: Implement logic to generate chat title from conversation
    return "New Chat"


async def create_chat(user_id: str) -> str:
    """Create a new AI chat for a user.
    
    Args:
        user_id: The user's ID
        
    Returns:
        str: The created chat's ID
    """
    try:
        user_object_id = PydanticObjectId(user_id)
        chat = AIChat(
            user_id=user_object_id,
            title=await generate_chat_title()
        )
        await chat.insert()
        logger.info("Created new chat %s for user %s", str(chat.id), user_id)
        return str(chat.id)
    except Exception as e:
        logger.error("Error creating chat for user %s: %s", user_id, e)
        raise


async def send_message(user_id: str, chat_id: str, message: str, model_name: str) -> str:
    """Send a message to an AI chat and get the AI response.
    
    Args:
        user_id: The user's ID
        chat_id: The chat's ID
        message: The user's message
        model_name: The AI model to use
        
    Returns:
        str: The AI's response text
        
    Raises:
        PermissionError: If user is not allowed to use the model
        ValueError: If chat is not found or doesn't belong to user
    """
    try:
        # Check if user can use the model
        has_permission = await check_model_permission(user_id, model_name)
        if not has_permission:
            logger.warning("User %s does not have permission to use model %s", user_id, model_name)
            raise PermissionError(f"User does not have permission to use model: {model_name}")
        
        # Find the chat
        user_object_id = PydanticObjectId(user_id)
        chat_object_id = PydanticObjectId(chat_id)
        chat = await AIChat.find_one(AIChat.id == chat_object_id)
        
        if not chat:
            raise ValueError(f"Chat not found: {chat_id}")
        
        if chat.user_id != user_object_id:
            raise ValueError("Chat does not belong to user")
        
        # Add user message
        user_message = ChatMessage(role="user", content=message, timestamp=datetime.utcnow())
        chat.messages.append(user_message)
        
        # Get AI response (placeholder for now)
        ai_response_text = await get_ai_response(message, model_name)
        
        # Add AI response
        ai_message = ChatMessage(role="assistant", content=ai_response_text, timestamp=datetime.utcnow())
        chat.messages.append(ai_message)
        
        # Update timestamp
        chat.updated_at = datetime.utcnow()
        
        await chat.save()
        logger.info("Added message to chat %s for user %s", chat_id, user_id)
        
        return ai_response_text
        
    except PermissionError:
        raise
    except ValueError:
        raise
    except Exception as e:
        logger.error("Error sending message to chat %s: %s", chat_id, e)
        raise


async def get_ai_response(message: str, model_name: str) -> str:
    """Get AI response for a message.
    
    This is a placeholder function that will be implemented later
    to actually call AI models.
    
    Args:
        message: The user's message
        model_name: The AI model to use
        
    Returns:
        str: The AI's response
    """
    # TODO: Implement actual AI model integration
    return "How can i help you"


async def get_user_chats(user_id: str) -> list:
    """Get all chats for a user.
    
    Args:
        user_id: The user's ID
        
    Returns:
        list: List of chat documents with id, title, messages, and timestamps
    """
    try:
        user_object_id = PydanticObjectId(user_id)
        chats = await AIChat.find(AIChat.user_id == user_object_id).sort("-updated_at").to_list()
        
        # Convert to dict format for response
        result = []
        for chat in chats:
            result.append({
                "id": str(chat.id),
                "title": chat.title,
                "messages": [
                    {
                        "id": str(i),  # Use index as id for now
                        "role": msg.role,
                        "content": msg.content,
                        "timestamp": msg.timestamp.isoformat()
                    }
                    for i, msg in enumerate(chat.messages)
                ],
                "created_at": chat.created_at.isoformat(),
                "updated_at": chat.updated_at.isoformat()
            })
        
        logger.info("Retrieved %d chats for user %s", len(result), user_id)
        return result
        
    except Exception as e:
        logger.error("Error getting chats for user %s: %s", user_id, e)
        raise
