"""AI models document for MongoDB with Beanie."""

from typing import List, Optional, Union
from datetime import datetime
from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field, field_validator
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
    
    @field_validator('models', mode='before')
    @classmethod
    def migrate_string_models(cls, v):
        """Migrate old string-based models to ModelInfo objects."""
        if isinstance(v, list):
            return [
                ModelInfo(name=m, alias=m, description="") if isinstance(m, str) else m
                for m in v
            ]
        return v
    
    class Settings:
        """Beanie document settings."""
        collection = "ai-models"
        indexes = [
            "user_id",  # Index on user_id for quick lookups
        ]


class ChatMessage(BaseModel):
    """Chat message model."""
    
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")


class AIChat(Document):
    """AI chat document.
    
    Stores chat conversations between users and AI models.
    """
    
    user_id: PydanticObjectId = Field(..., description="User ID reference")
    title: str = Field(default="New Chat", description="Chat title")
    messages: List[ChatMessage] = Field(default_factory=list, description="List of chat messages")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Chat creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Chat last update timestamp")
    
    class Settings:
        """Beanie document settings."""
        collection = "ai-chats"
        indexes = [
            "user_id",  # Index on user_id for efficient queries with many chats
            [("user_id", 1), ("updated_at", -1)],  # Compound index for user chats sorted by update time
        ]
