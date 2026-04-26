"""Schemas for AI chat message endpoints."""

from pydantic import BaseModel, Field
from typing import List


class ModelInfo(BaseModel):
    """Model information with alias and description."""
    
    name: str = Field(..., description="Model name/ID")
    alias: str = Field(..., description="Display alias for the model")
    description: str = Field(default="", description="Model description")


class ChatMessageRequest(BaseModel):
    """Request schema for AI chat message."""
    
    model_name: str = Field(..., description="Name of the AI model to use")
    message: str = Field(..., description="The message to send to the AI model")


class ChatMessageResponse(BaseModel):
    """Response schema for AI chat message."""
    
    model_name: str = Field(..., description="Name of the AI model used")
    text: str = Field(..., description="The response text from the AI model")


class AvailableModelsResponse(BaseModel):
    """Response schema for available models."""
    
    models: List[ModelInfo] = Field(..., description="List of available AI model info for the user")
