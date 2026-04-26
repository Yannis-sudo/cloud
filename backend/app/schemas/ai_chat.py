"""Schemas for AI chat message endpoints."""

from pydantic import BaseModel, Field


class ChatMessageRequest(BaseModel):
    """Request schema for AI chat message."""
    
    model_name: str = Field(..., description="Name of the AI model to use")
    message: str = Field(..., description="The message to send to the AI model")


class ChatMessageResponse(BaseModel):
    """Response schema for AI chat message."""
    
    model_name: str = Field(..., description="Name of the AI model used")
    text: str = Field(..., description="The response text from the AI model")
