"""AI models document for MongoDB with Beanie."""

from typing import List
from beanie import Document, PydanticObjectId
from pydantic import Field
from pymongo.collation import Collation


class ModelCatalog(Document):
    """Model catalog document.
    
    Stores lists of AI models by type (free, paid, etc.).
    """
    
    type: str = Field(..., description="Type of models (e.g., 'free-models', 'paid-models')")
    models: List[str] = Field(default_factory=list, description="List of AI model names")
    
    class Settings:
        """Beanie document settings."""
        collection = "model-catalog"
        indexes = [
            "type",  # Index on type for quick lookups
        ]


class UserAIModels(Document):
    """User AI models permission document.
    
    Stores the list of AI models that a user is allowed to use.
    """
    
    user_id: PydanticObjectId = Field(..., description="User ID reference")
    models: List[str] = Field(default_factory=list, description="List of allowed AI model names")
    
    class Settings:
        """Beanie document settings."""
        collection = "ai-models"
        indexes = [
            "user_id",  # Index on user_id for quick lookups
        ]
