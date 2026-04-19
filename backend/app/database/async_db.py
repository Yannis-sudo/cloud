"""Async MongoDB database setup with Motor and Beanie."""

import logging
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from beanie import init_beanie
from app.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

# Global Motor client instance
_motor_client: Optional[AsyncIOMotorClient] = None


async def get_motor_client() -> AsyncIOMotorClient:
    """Get or create async Motor client instance.
    
    Returns:
        AsyncIOMotorClient: Motor client for async MongoDB operations
        
    Raises:
        Exception: If connection fails
    """
    global _motor_client
    
    if _motor_client is None:
        try:
            _motor_client = AsyncIOMotorClient(
                settings.DATABASE_URL,
                serverSelectionTimeoutMS=5000,
                maxPoolSize=50,
                retryWrites=True,
                w="majority",
                connectTimeoutMS=10000,
                socketTimeoutMS=30000,
                uuidRepresentation="standard",  # Important for Beanie
            )
            
            # Test connection
            await _motor_client.admin.command("ping")
            logger.info("Async MongoDB (Motor) connection established successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise Exception(f"Database connection failed: {e}")
    
    return _motor_client


async def get_database() -> AsyncIOMotorDatabase:
    """Get async MongoDB database instance.
    
    Returns:
        AsyncIOMotorDatabase: Motor database instance
    """
    client = await get_motor_client()
    return client[settings.DATABASE_NAME]


async def init_db(document_models: list) -> None:
    """Initialize Beanie with document models.
    
    Args:
        document_models: List of Beanie document models to initialize
        
    Raises:
        Exception: If Beanie initialization fails
    """
    try:
        connection_string = f"{settings.DATABASE_URL.rstrip('/')}/{settings.DATABASE_NAME}"
        await init_beanie(connection_string=connection_string, document_models=document_models)
        logger.info("Beanie initialized successfully with all document models")
    except Exception as e:
        logger.error(f"Failed to initialize Beanie: {e}")
        raise Exception(f"Beanie initialization failed: {e}")


async def close_db() -> None:
    """Close the Motor client connection."""
    global _motor_client
    
    if _motor_client is not None:
        try:
            _motor_client.close()
            _motor_client = None
            logger.info("Async MongoDB (Motor) connection closed")
        except Exception as e:
            logger.error(f"Error closing Motor connection: {e}")
