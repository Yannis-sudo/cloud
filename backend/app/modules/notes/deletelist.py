"""Delete list functionality for removing lists and cleaning up permissions."""

import logging
from typing import Dict, Any
from pymongo import errors
from bson import ObjectId

from app.database import get_mongo_client

logger = logging.getLogger(__name__)


def get_notes_database():
    """Get the notes database (separate from the main cloud database)."""
    try:
        client = get_mongo_client()
        return client["notes"]
    except Exception as e:
        logger.error(f"Error connecting to notes database: {e}")
        raise


def delete_list(email: str, password: str, list_id: str) -> Dict[str, Any]:
    """Delete a list and clean up associated permissions.
    
    Args:
        email: The email of the authenticated user
        password: The password for authentication
        list_id: The ID of the list to delete
        
    Returns:
        dict: Contains success message and deleted list_id
        
    Raises:
        ValueError: If user not found, lacks permissions, or list not found
        Exception: For database errors
    """
    try:
        db = get_notes_database()
        
        # Validate and convert list_id to ObjectId
        try:
            object_id = ObjectId(list_id)
        except Exception as e:
            raise ValueError(f"Invalid list ID format: {list_id}")
        
        # Get the list to check permissions and get details
        list_collection = db.lists
        list_doc = list_collection.find_one({"_id": object_id})
        
        if not list_doc:
            raise ValueError(f"List not found: {list_id}")
        
        # Check if user is admin of this list
        admins = list_doc.get("admins", [])
        user_email_lower = email.lower()
        
        if user_email_lower not in [admin.lower() for admin in admins]:
            raise ValueError("User does not have admin permissions for this list")
        
        # Delete the list
        delete_result = list_collection.delete_one({"_id": object_id})
        
        if delete_result.deleted_count == 0:
            raise ValueError(f"Failed to delete list: {list_id}")
        
        # Clean up permissions - remove the list from all user permissions
        permissions_collection = db.noteslist_permissions
        permission_update_result = permissions_collection.update_many(
            {},
            {"$unset": {f"lists.{list_id}": ""}}
        )
        
        logger.info(f"Deleted list {list_id} and cleaned up permissions for {permission_update_result.modified_count} users")
        
        return {
            "message": "List deleted successfully",
            "list_id": list_id
        }
        
    except ValueError:
        # Re-raise ValueError (validation errors)
        raise
    except errors.PyMongoError as e:
        logger.error(f"Database error while deleting list {list_id}: {e}")
        raise Exception(f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in delete_list: {e}")
        raise Exception(f"Failed to delete list: {str(e)}")
