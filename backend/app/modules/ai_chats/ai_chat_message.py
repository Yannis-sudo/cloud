"""AI chat message module functions."""

import logging
from beanie import PydanticObjectId
from app.modules.ai_chats.models import UserAIModels, ModelCatalog

logger = logging.getLogger(__name__)


async def get_free_models() -> list[str]:
    """Get the list of free AI models from the model catalog.
    
    Returns:
        list[str]: List of free model names
    """
    try:
        catalog = await ModelCatalog.find_one(ModelCatalog.type == "free-models")
        if catalog:
            logger.info(f"[DEBUG] Free models loaded from catalog: {catalog.models}")
            return catalog.models
        logger.info("[DEBUG] No free-models entry found in catalog")
        return []
    except Exception as e:
        logger.error(f"[DEBUG] Error fetching free models: {e}")
        return []


async def ensure_user_has_models(user_id: str) -> list[str]:
    """Ensure user has AI models configured, auto-create from free models if not.
    Also adds any new free models to existing user entries.
    
    Args:
        user_id: The user's ID
        
    Returns:
        list[str]: List of available model names for the user
    """
    try:
        user_object_id = PydanticObjectId(user_id)
        user_ai_models = await UserAIModels.find_one(UserAIModels.user_id == user_object_id)
        free_models = await get_free_models()
        
        if not user_ai_models:
            # User has no AI models configured, create entry with free models (or empty list)
            user_ai_models = UserAIModels(user_id=user_object_id, models=free_models if free_models else [])
            await user_ai_models.insert()
            logger.info(f"[DEBUG] Created new user entry for user {user_id} with models: {user_ai_models.models}")
            return user_ai_models.models
        
        # User has an entry, check if we need to add new free models
        if free_models:
            current_models = set(user_ai_models.models)
            free_models_set = set(free_models)
            
            # Add any free models that are not in the user's current list
            missing_models = free_models_set - current_models
            if missing_models:
                # Add missing free models to user's list
                user_ai_models.models.extend(missing_models)
                await user_ai_models.save()
                logger.info(f"[DEBUG] Added missing free models {missing_models} to user {user_id}")
        
        logger.info(f"[DEBUG] Returning models for user {user_id}: {user_ai_models.models}")
        return user_ai_models.models
    except Exception as e:
        logger.error(f"[DEBUG] Error ensuring user has models: {e}")
        return []


async def check_model_permission(user_id: str, model_name: str) -> bool:
    """Check if a user is allowed to use a specific AI model.
    Also ensures user has all free models before checking.
    
    Args:
        user_id: The user's ID
        model_name: The name of the AI model to check
        
    Returns:
        bool: True if user is allowed to use the model, False otherwise
    """
    try:
        # First ensure user has all free models
        user_models = await ensure_user_has_models(user_id)
        
        # Then check if the requested model is in the user's list
        return model_name in user_models
    except Exception:
        # Invalid user ID or other error
        return False


async def get_user_available_models(user_id: str) -> list[str]:
    """Get the list of AI models available for a user.
    
    Args:
        user_id: The user's ID
        
    Returns:
        list[str]: List of available model names
    """
    return await ensure_user_has_models(user_id)
