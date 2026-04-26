"""AI models document for MongoDB with Beanie."""

from typing import List, Optional
from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field
from pymongo.collation import Collation


class ModelInfo(BaseModel):
    """Model information with alias and description."""
    
    name: str = Field(..., description="Model name/ID")
    alias: str = Field(..., description="Display alias for the model")
    description: str = Field(default="", description="Model description")


class ModelCatalog(Document):
    """Model catalog document.
    
    Stores lists of AI models by type (free, paid, etc.).
    """
    
    type: str = Field(..., description="Type of models (e.g., 'free-models', 'paid-models')")
    models: List[ModelInfo] = Field(default_factory=list, description="List of AI model info")
    
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
    models: List[ModelInfo] = Field(default_factory=list, description="List of allowed AI model info")
    
    class Settings:
        """Beanie document settings."""
        collection = "ai-models"
        indexes = [
            "user_id",  # Index on user_id for quick lookups
        ]
