"""Permission management functionality."""

import logging
from typing import Dict, Any, Optional
from pymongo import errors
from pymongo.results import UpdateResult, InsertOneResult
from bson import ObjectId

from app.database import get_mongo_client, get_database

logger = logging.getLogger(__name__)


def get_notes_database():
    """Get the notes database (separate from the main cloud database)."""
    try:
        client = get_mongo_client()
        return client["notes"]
    except Exception as e:
        logger.error(f"Error connecting to notes database: {e}")
        raise


def is_list_admin(user_email: str, list_id: str) -> bool:
    """Check if user is an admin of the specified list.
    
    Args:
        user_email: The email of the user to check
        list_id: The ObjectId of the list as string
        
    Returns:
        True if user is admin, False otherwise
    """
    try:
        db = get_notes_database()
        
        # Convert list_id to ObjectId for querying
        try:
            object_id = ObjectId(list_id)
        except Exception:
            logger.warning(f"Invalid list_id format: {list_id}")
            return False
        
        # Find the list and check if user is in admins array
        list_doc = db.lists.find_one({
            "_id": object_id,
            "admins": user_email.lower()
        })
        
        return list_doc is not None
        
    except Exception as e:
        logger.error(f"Error checking admin status for {user_email} on list {list_id}: {e}")
        return False


def user_exists(user_email: str) -> Optional[Dict[str, Any]]:
    """Check if user exists in the main users collection.
    
    Args:
        user_email: The email of the user to check
        
    Returns:
        User document if exists, None otherwise
    """
    try:
        db = get_database()
        
        user_doc = db.users.find_one({
            "email": user_email.lower()
        })
        
        return user_doc
        
    except Exception as e:
        logger.error(f"Error checking user existence for {user_email}: {e}")
        return None


def get_current_permissions(user_email: str, list_id: str) -> Optional[Dict[str, Any]]:
    """Get current permissions for a user on a specific list.
    
    Args:
        user_email: The email of the user
        list_id: The ObjectId of the list as string
        
    Returns:
        Current permissions dict if exists, None otherwise
    """
    try:
        db = get_notes_database()
        
        permissions_doc = db.noteslist_permissions.find_one({
            "email": user_email.lower()
        })
        
        if permissions_doc and "lists" in permissions_doc:
            return permissions_doc["lists"].get(list_id, {})
        
        return None
        
    except Exception as e:
        logger.error(f"Error getting current permissions for {user_email} on list {list_id}: {e}")
        return None


def create_permissions_entry(user_email: str, list_id: str, permissions: Dict[str, bool]) -> Optional[InsertOneResult]:
    """Create a new permissions entry for a user.
    
    Args:
        user_email: The email of the user
        list_id: The ObjectId of the list as string
        permissions: The permissions to set
        
    Returns:
        InsertOneResult if successful, None otherwise
    """
    try:
        db = get_notes_database()
        
        # Get username from users collection
        user_doc = user_exists(user_email)
        username = user_doc.get("username", "") if user_doc else ""
        
        permissions_entry = {
            "email": user_email.lower(),
            "username": username,
            "lists": {
                list_id: permissions
            }
        }
        
        result = db.noteslist_permissions.insert_one(permissions_entry)
        logger.info(f"Created permissions entry for {user_email} on list {list_id}")
        return result
        
    except errors.DuplicateKeyError:
        logger.warning(f"Permissions entry already exists for {user_email}")
        return None
    except Exception as e:
        logger.error(f"Error creating permissions entry for {user_email} on list {list_id}: {e}")
        return None


def update_user_permissions(user_email: str, list_id: str, permissions: Dict[str, bool]) -> Optional[UpdateResult]:
    """Update user permissions for a specific list.
    
    Args:
        user_email: The email of the user
        list_id: The ObjectId of the list as string
        permissions: The permissions to set (partial update)
        
    Returns:
        UpdateResult if successful, None otherwise
    """
    try:
        db = get_notes_database()
        
        # Get current permissions to merge with new ones
        current_permissions = get_current_permissions(user_email, list_id) or {}
        
        # Merge permissions (partial update)
        merged_permissions = {**current_permissions, **permissions}
        
        # Update permissions
        result = db.noteslist_permissions.update_one(
            {"email": user_email.lower()},
            {
                "$set": {
                    f"lists.{list_id}": merged_permissions,
                    "updated_at": None  # Will be set by MongoDB
                }
            },
            upsert=True
        )
        
        logger.info(f"Updated permissions for {user_email} on list {list_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error updating permissions for {user_email} on list {list_id}: {e}")
        return None


def validate_permissions(permissions: Dict[str, Any]) -> bool:
    """Validate the permissions object.
    
    Args:
        permissions: The permissions object to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        valid_keys = {"can_view", "can_create", "can_edit", "can_delete"}
        
        # Check if all provided keys are valid permission keys
        provided_keys = set(permissions.keys())
        invalid_keys = provided_keys - valid_keys
        
        if invalid_keys:
            logger.warning(f"Invalid permission keys: {invalid_keys}")
            return False
        
        # Check if all provided values are booleans
        for key in provided_keys:
            if not isinstance(permissions[key], bool):
                logger.warning(f"Permission {key} is not a boolean: {permissions[key]}")
                return False
        
        # At least one permission key should be provided
        if len(provided_keys) == 0:
            logger.warning("No permission keys provided")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error validating permissions: {e}")
        return False


def update_permissions(requesting_email: str, requesting_password: str, list_id: str, 
                       target_user_email: str, permissions: Dict[str, bool]) -> Dict[str, Any]:
    """Update permissions for a user on a specific list.
    
    Args:
        requesting_email: The email of the user making the request
        requesting_password: The password of the user making the request
        list_id: The ObjectId of the list as string
        target_user_email: The email of the user to update permissions for
        permissions: The permissions to set
        
    Returns:
        dict: Contains success status and updated permissions
        
    Raises:
        ValueError: If validation fails
        Exception: For database errors or authorization issues
    """
    try:
        # Validate inputs
        if not list_id or not list_id.strip():
            raise ValueError("List ID is required")
        
        if not target_user_email or not target_user_email.strip():
            raise ValueError("Target user email is required")
        
        if not validate_permissions(permissions):
            raise ValueError("Invalid permissions format")
        
        # Normalize emails
        requesting_email = requesting_email.lower()
        target_user_email = target_user_email.lower()
        
        # Check if requesting user is admin of the list
        if not is_list_admin(requesting_email, list_id):
            raise ValueError("You are not authorized to manage permissions for this list")
        
        # Check if target user exists
        target_user = user_exists(target_user_email)
        if not target_user:
            raise ValueError(f"User {target_user_email} does not exist")
        
        # Update permissions
        result = update_user_permissions(target_user_email, list_id, permissions)
        
        if result is None:
            raise Exception("Failed to update permissions in database")
        
        # Get updated permissions for response
        updated_permissions = get_current_permissions(target_user_email, list_id) or permissions
        
        logger.info(f"Successfully updated permissions for {target_user_email} on list {list_id} by {requesting_email}")
        
        return {
            "success": True,
            "target_user_email": target_user_email,
            "list_id": list_id,
            "updated_permissions": updated_permissions
        }
        
    except ValueError:
        # Re-raise ValueError (validation errors)
        raise
    except Exception as e:
        logger.error(f"Unexpected error in update_permissions: {e}")
        raise Exception(f"Failed to update permissions: {str(e)}")
