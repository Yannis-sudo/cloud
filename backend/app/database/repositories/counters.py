"""Counters repository for atomic ID generation."""

import logging
from typing import Dict, Any, Optional

from app.database.repositories.base import BaseRepository
from app.core.exceptions import DatabaseError

logger = logging.getLogger(__name__)


class CountersRepository(BaseRepository):
    """Repository for counter operations."""
    
    def __init__(self):
        """Initialize counters repository."""
        super().__init__("counters")
    
    async def get_next_sequence(self, collection_name: str) -> int:
        """Get the next sequence number for a collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            int: Next sequence number
            
        Raises:
            DatabaseError: If operation fails
        """
        try:
            # Use MongoDB's find_one_and_update for atomic increment
            counter = self.collection.find_one_and_update(
                {"_id": collection_name},
                {"$inc": {"seq": 1}},
                upsert=True,
                return_document=True
            )
            
            return counter["seq"]
            
        except Exception as e:
            logger.error(f"Error getting next sequence for {collection_name}: {e}")
            raise DatabaseError(f"Failed to get next sequence: {e}")
    
    async def reset_counter(self, collection_name: str, value: int = 1) -> bool:
        """Reset a counter to a specific value.
        
        Args:
            collection_name: Name of the collection
            value: New counter value
            
        Returns:
            bool: True if reset successfully
        """
        try:
            result = self.collection.update_one(
                {"_id": collection_name},
                {"$set": {"seq": value}},
                upsert=True
            )
            
            return result.acknowledged
            
        except Exception as e:
            logger.error(f"Error resetting counter for {collection_name}: {e}")
            raise DatabaseError(f"Failed to reset counter: {e}")
    
    async def get_current_sequence(self, collection_name: str) -> Optional[int]:
        """Get the current sequence value for a collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Optional[int]: Current sequence value or None if not found
        """
        try:
            counter = self.collection.find_one({"_id": collection_name})
            return counter["seq"] if counter else None
            
        except Exception as e:
            logger.error(f"Error getting current sequence for {collection_name}: {e}")
            return None
    
    async def get_all_counters(self) -> Dict[str, int]:
        """Get all counters.
        
        Returns:
            Dict[str, int]: Dictionary of all counters
        """
        try:
            counters = {}
            for counter in self.collection.find({}):
                counters[counter["_id"]] = counter["seq"]
            
            return counters
            
        except Exception as e:
            logger.error(f"Error getting all counters: {e}")
            return {}
    
    def get_model_schema(self) -> Dict[str, Any]:
        """Get counters model schema.
        
        Returns:
            Dict[str, Any]: Counters model schema
        """
        return {
            "type": "object",
            "properties": {
                "_id": {"type": "string"},
                "seq": {"type": "integer", "minimum": 1}
            },
            "required": ["_id", "seq"],
            "additionalProperties": False
        }
