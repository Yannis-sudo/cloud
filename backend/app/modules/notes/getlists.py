"""Get lists functionality for retrieving user-accessible lists."""

import logging
from typing import Dict, Any, List, Optional
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


def get_user_viewable_lists(email: str, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """Get all lists that a user has permission to view.
    
    Args:
        email: The email of the authenticated user
        page: Page number for pagination (1-based)
        page_size: Number of items per page
        
    Returns:
        dict: Contains lists array and pagination metadata
        
    Raises:
        ValueError: If user not found or has no permissions
        Exception: For database errors
    """
    try:
        db = get_notes_database()
        
        # Get user's permissions from noteslist_permissions collection
        user_permissions = db.noteslist_permissions.find_one({"email": email.lower()})
        
        if not user_permissions:
            raise ValueError(f"No permissions found for user: {email}")
        
        # Extract list IDs where can_view is true
        user_lists = user_permissions.get("lists", {})
        viewable_list_ids = [
            list_id for list_id, perms in user_lists.items() 
            if perms.get("can_view", False)
        ]
        
        if not viewable_list_ids:
            # User has no viewable lists
            return {
                "lists": [],
                "total_count": 0,
                "page": page,
                "page_size": page_size,
                "total_pages": 0
            }
        
        # Convert list IDs to ObjectId for MongoDB query
        object_ids = []
        for list_id in viewable_list_ids:
            try:
                object_ids.append(ObjectId(list_id))
            except Exception as e:
                logger.warning(f"Invalid ObjectId format for list_id {list_id}: {e}")
                continue
        
        if not object_ids:
            # No valid ObjectIds found
            return {
                "lists": [],
                "total_count": 0,
                "page": page,
                "page_size": page_size,
                "total_pages": 0
            }
        
        # Calculate pagination
        skip_count = (page - 1) * page_size
        total_count = len(object_ids)
        total_pages = (total_count + page_size - 1) // page_size
        
        # Fetch full list details with pagination
        lists_cursor = db.lists.find({"_id": {"$in": object_ids}})
        
        # Apply pagination
        lists_cursor = lists_cursor.skip(skip_count).limit(page_size)
        
        # Convert MongoDB documents to list format
        lists_data = []
        for list_doc in lists_cursor:
            # Convert ObjectId to string for response
            list_info = {
                "list_id": str(list_doc["_id"]),
                "list_name": list_doc.get("list_name", ""),
                "description": list_doc.get("description", ""),
                "created_by": list_doc.get("created_by", ""),
                "admins": list_doc.get("admins", []),
                "created_at": str(list_doc.get("created_at")) if list_doc.get("created_at") else None,
                "updated_at": str(list_doc.get("updated_at")) if list_doc.get("updated_at") else None
            }
            lists_data.append(list_info)
        
        logger.info(f"Retrieved {len(lists_data)} lists for user {email} (page {page}/{total_pages})")
        
        return {
            "lists": lists_data,
            "total_count": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
        
    except ValueError:
        # Re-raise ValueError (validation errors)
        raise
    except errors.PyMongoError as e:
        logger.error(f"Database error while getting lists for {email}: {e}")
        raise Exception(f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in get_user_viewable_lists: {e}")
        raise Exception(f"Failed to retrieve lists: {str(e)}")


def get_lists(email: str, password: str, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """Get lists for a user with authentication check.
    
    Args:
        email: The email of the authenticated user
        password: The password for authentication
        page: Page number for pagination (1-based)
        page_size: Number of items per page
        
    Returns:
        dict: Contains lists array and pagination metadata
        
    Raises:
        ValueError: If authentication fails or user not found
        Exception: For database errors
    """
    try:
        # Validate pagination parameters
        if page < 1:
            raise ValueError("Page must be greater than 0")
        if page_size < 1 or page_size > 100:
            raise ValueError("Page size must be between 1 and 100")
        
        # Get user's viewable lists
        result = get_user_viewable_lists(email, page, page_size)
        
        return result
        
    except ValueError:
        # Re-raise ValueError (validation errors)
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_lists: {e}")
        raise Exception(f"Failed to get lists: {str(e)}")
