"""AI chat message module functions."""

from beanie import PydanticObjectId
from app.modules.ai_chats.models import UserAIModels, ModelCatalog


async def get_free_models() -> list[str]:
    """Get the list of free AI models from the model catalog.
    
    Returns:
        list[str]: List of free model names
    """
    try:
        catalog = await ModelCatalog.find_one(ModelCatalog.type == "free-models")
        if catalog:
            return catalog.models
        return []
    except Exception:
        return []


async def ensure_user_has_models(user_id: str) -> list[str]:
    """Ensure user has AI models configured, auto-create from free models if not.
    
    Args:
        user_id: The user's ID
        
    Returns:
        list[str]: List of available model names for the user
    """
    try:
        user_object_id = PydanticObjectId(user_id)
        user_ai_models = await UserAIModels.find_one(UserAIModels.user_id == user_object_id)
        
        if not user_ai_models:
            # User has no AI models configured, create from free models
            free_models = await get_free_models()
            if free_models:
                user_ai_models = UserAIModels(user_id=user_object_id, models=free_models)
                await user_ai_models.insert()
                return free_models
            return []
        
        return user_ai_models.models
    except Exception:
        return []


async def check_model_permission(user_id: str, model_name: str) -> bool:
    """Check if a user is allowed to use a specific AI model.
    
    Args:
        user_id: The user's ID
        model_name: The name of the AI model to check
        
    Returns:
        bool: True if user is allowed to use the model, False otherwise
    """
    try:
        user_object_id = PydanticObjectId(user_id)
        user_ai_models = await UserAIModels.find_one(UserAIModels.user_id == user_object_id)
        
        if not user_ai_models:
            # User has no AI models configured, auto-create from free models
            free_models = await get_free_models()
            if free_models and model_name in free_models:
                user_ai_models = UserAIModels(user_id=user_object_id, models=free_models)
                await user_ai_models.insert()
                return True
            return False
        
        return model_name in user_ai_models.models
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
