"""Dependency injection for FastAPI."""

from typing import Generator
from fastapi import HTTPException, status
from pymongo import MongoClient
from pymongo.database import Database
from bson import ObjectId

from app.core.exceptions import DatabaseError
from app.database.connection import get_database, get_mongo_client


def get_db() -> Generator[Database, None, None]:
    """Get database dependency.
    
    Yields:
        Database: MongoDB database instance
    """
    try:
        db = get_database()
        yield db
    except Exception as e:
        raise DatabaseError(f"Database connection failed: {str(e)}")


def get_mongo_client_dep() -> Generator[MongoClient, None, None]:
    """Get MongoDB client dependency.
    
    Yields:
        MongoClient: MongoDB client instance
    """
    try:
        client = get_mongo_client()
        yield client
    except Exception as e:
        raise DatabaseError(f"MongoDB client connection failed: {str(e)}")


def validate_object_id(id: str) -> ObjectId:
    """Validate and convert string to ObjectId.

    Args:
        id: String ID to validate

    Returns:
        ObjectId: Valid ObjectId

    Raises:
        HTTPException: If ID is invalid
    """
    try:
        return ObjectId(id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid ID format: {id}"
        )
