"""Get permissions functionality."""

import logging
from typing import Dict, Any, List, Optional
from pymongo import errors
from bson import ObjectId

from app.database import get_mongo_client, get_database

# Import the is_list_admin function from updatepermissions module
from app.modules.notes.updatepermissions import is_list_admin

logger = logging.getLogger(__name__)


def get_notes_database():
    """Get the notes database (separate from the main cloud database)."""
    try:
        client = get_mongo_client()
        return client["notes"]
    except Exception as e:
        logger.error(f"Error connecting to notes database: {e}")
        raise


def get_list_permissions(list_id: str) -> List[Dict[str, Any]]:
    """Get all users with permissions for a specific list.
    
    Args:
        list_id: The ObjectId of the list as string
        
    Returns:
        List of user permission documents
    """
    try:
        db = get_notes_database()
        
        # Find all users who have permissions for this list
        permissions_cursor = db.noteslist_permissions.find({
            f"lists.{list_id}": {"$exists": True}
        })
        
        users_with_permissions = []
        
        for doc in permissions_cursor:
            user_email = doc.get("email", "")
            username = doc.get("username", "")
            permissions = doc.get("lists", {}).get(list_id, {})
            
            users_with_permissions.append({
                "email": user_email,
                "username": username,
                "permissions": permissions
            })
        
        logger.info(f"Found {len(users_with_permissions)} users with permissions for list {list_id}")
        return users_with_permissions
        
    except Exception as e:
        logger.error(f"Error getting permissions for list {list_id}: {e}")
        return []


def enrich_user_data(users_with_permissions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Enrich user data with usernames from users collection.
    
    Args:
        users_with_permissions: List of users with basic permission data
        
    Returns:
        List of users with enriched data
    """
    try:
        db = get_database()
        
        enriched_users = []
        
        for user in users_with_permissions:
            user_email = user.get("email", "")
            
            # Get user details from main users collection
            user_doc = db.users.find_one({
                "email": user_email.lower()
            })
            
            if user_doc:
                username = user_doc.get("username", "")
                enriched_user = {
                    "email": user_email,
                    "username": username,
                    "permissions": user.get("permissions", {})
                }
                enriched_users.append(enriched_user)
            else:
                # Keep original data if user not found in main collection
                enriched_users.append(user)
        
        return enriched_users
        
    except Exception as e:
        logger.error(f"Error enriching user data: {e}")
        return users_with_permissions


def get_permissions(requesting_email: str, requesting_password: str, list_id: str) -> Dict[str, Any]:
    """Get all users with permissions for a specific list.
    
    Args:
        requesting_email: The email of the user making the request
        requesting_password: The password of the user making the request
        list_id: The ObjectId of the list as string
        
    Returns:
        dict: Contains success status and list of users with permissions
        
    Raises:
        ValueError: If validation fails
        Exception: For database errors or authorization issues
    """
    try:
        # Validate inputs
        if not list_id or not list_id.strip():
            raise ValueError("List ID is required")
        
        # Normalize email
        requesting_email = requesting_email.lower()
        
        # Check if requesting user is admin of the list
        if not is_list_admin(requesting_email, list_id):
            raise ValueError("You are not authorized to view permissions for this list")
        
        # Get all users with permissions for this list
        users_with_permissions = get_list_permissions(list_id)
        
        # Enrich user data with usernames
        enriched_users = enrich_user_data(users_with_permissions)
        
        logger.info(f"Successfully retrieved permissions for list {list_id} by {requesting_email}")
        
        return {
            "success": True,
            "list_id": list_id,
            "users": enriched_users
        }
        
    except ValueError:
        # Re-raise ValueError (validation errors)
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_permissions: {e}")
        raise Exception(f"Failed to get permissions: {str(e)}")
