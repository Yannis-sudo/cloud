"""Schemas for AI chat message endpoints."""

from pydantic import BaseModel, Field
from typing import List, Optional
from app.modules.ai_chats.models import ModelInfo


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


class CreateChatRequest(BaseModel):
    """Request schema for creating a new chat."""
    
    pass  # No parameters needed


class CreateChatResponse(BaseModel):
    """Response schema for creating a new chat."""
    
    chat_id: str = Field(..., description="The ID of the created chat")
    title: str = Field(..., description="The title of the created chat")


class SendMessageRequest(BaseModel):
    """Request schema for sending a message to a chat."""
    
    chat_id: str = Field(..., description="The ID of the chat")
    model_name: str = Field(..., description="Name of the AI model to use")
    message: str = Field(..., description="The message to send to the AI model")


class ChatMessage(BaseModel):
    """Chat message schema."""
    
    id: str = Field(..., description="Message ID")
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: str = Field(..., description="Message timestamp (ISO format)")


class ChatData(BaseModel):
    """Chat data schema."""
    
    id: str = Field(..., description="Chat ID")
    title: str = Field(..., description="Chat title")
    messages: List[ChatMessage] = Field(default_factory=list, description="List of chat messages")
    created_at: str = Field(..., description="Chat creation timestamp (ISO format)")
    updated_at: str = Field(..., description="Chat last update timestamp (ISO format)")


class GetChatsResponse(BaseModel):
    """Response schema for getting user's chats."""
    
    chats: List[ChatData] = Field(..., description="List of user's chats")
