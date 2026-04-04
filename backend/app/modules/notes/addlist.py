"""List management functionality."""

import logging
from typing import Dict, Any, Optional
from pymongo import errors
from pymongo.results import InsertOneResult, UpdateResult
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


def create_list_in_db(list_name: str, creator_email: str, description: str = "") -> Optional[InsertOneResult]:
    """Create a new list in database with unique ID.
    
    Args:
        list_name: The name of list to create
        creator_email: The email of user creating list
        description: Optional description of list
        
    Returns:
        InsertOneResult if successful, None otherwise
    """
    try:
        db = get_notes_database()
        
        list_document = {
            "_id": ObjectId(),  # Generate unique ObjectId
            "list_name": list_name,
            "description": description,
            "created_by": creator_email.lower(),
            "admins": [creator_email.lower()],
            "created_at": None,  # Will be set by MongoDB
            "updated_at": None   # Will be set by MongoDB
        }
        
        result = db.lists.insert_one(list_document)
        logger.info(f"Successfully created list '{list_name}' by {creator_email} with ID {list_document['_id']}")
        return result
        
    except errors.PyMongoError as e:
        logger.error(f"Database error while creating list '{list_name}': {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error while creating list '{list_name}': {e}")
        return None


def add_user_permissions_for_list(user_email: str, list_id: str, is_admin: bool = True) -> Optional[UpdateResult]:
    """Add or update user permissions for a specific list using list_id.
    
    Args:
        user_email: The email of the user
        list_id: The ObjectId of the list as string
        is_admin: Whether the user should have admin permissions for this list
        
    Returns:
        UpdateResult if successful, None otherwise
    """
    try:
        db = get_notes_database()
        
        # Set up permissions based on admin status
        if is_admin:
            list_permissions = {
                "can_view": True,
                "can_create": True,
                "can_edit": True,
                "can_delete": True
            }
        else:
            list_permissions = {
                "can_view": True,
                "can_create": False,
                "can_edit": False,
                "can_delete": False
            }
        
        # Update user permissions using list_id
        result = db.noteslist_permissions.update_one(
            {"email": user_email.lower()},
            {
                "$set": {
                    f"lists.{list_id}": list_permissions,
                    "updated_at": None  # Will be set by MongoDB
                }
            },
            upsert=True
        )
        
        logger.info(f"Added permissions for {user_email} on list ID {list_id}")
        return result
        
    except errors.PyMongoError as e:
        logger.error(f"Database error while adding permissions for {user_email} on list ID {list_id}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error while adding permissions for {user_email} on list ID {list_id}: {e}")
        return None


def add_list(email: str, password: str, list_name: str, creator_email: str, description: str = ""):
    """Add a new list to the system with admin permissions for the creator.
    
    Args:
        email: The email of the authenticated user
        password: The password of the authenticated user
        list_name: The name of list to create
        creator_email: The email of the user creating the list
        description: Optional description of the list
        
    Returns:
        dict: Contains list_id and list_name if successful
        
    Raises:
        ValueError: If validation fails
        Exception: For database errors
    """
    try:
        # Validate input
        if not list_name or not list_name.strip():
            raise ValueError("List name is required")
        
        if not creator_email:
            raise ValueError("Creator email is required")
        
        list_name = list_name.strip()
        creator_email = creator_email.lower()
        
        # Create list in database
        list_result = create_list_in_db(list_name, creator_email, description)
        
        if list_result is None:
            raise Exception("Failed to create list in database")
        
        # Get the generated list_id
        list_id = str(list_result.inserted_id)
        
        # Add creator permissions for the list
        permissions_result = add_user_permissions_for_list(creator_email, list_id, is_admin=True)
        
        if permissions_result is None:
            logger.warning(f"List '{list_name}' created but failed to add permissions for {creator_email}")
        
        logger.info(f"List '{list_name}' successfully created by {creator_email} with ID {list_id}")
        
        # Return list information for response
        return {
            "list_id": list_id,
            "list_name": list_name
        }
        
    except ValueError:
        # Re-raise ValueError (validation errors)
        raise
    except Exception as e:
        logger.error(f"Unexpected error in add_list: {e}")
        raise Exception(f"Failed to add list: {str(e)}")
