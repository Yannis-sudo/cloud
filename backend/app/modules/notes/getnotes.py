"""Get notes functionality for retrieving notes from specific lists."""

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


def check_user_list_view_permission(email: str, list_id: str) -> Dict[str, Any]:
    """Check if user has permission to view notes in the specified list.
    
    Args:
        email: The email address of the user
        list_id: The ObjectId of the list to check permissions for
        
    Returns:
        Dict containing permission status and details
    """
    try:
        db = get_notes_database()
        
        # Check if list exists by ID
        try:
            object_id = ObjectId(list_id)
            list_info = db.lists.find_one({"_id": object_id})
        except:
            return {"has_permission": False, "message": f"Invalid list ID: {list_id}"}
        
        if not list_info:
            return {"has_permission": False, "message": f"List with ID '{list_id}' does not exist"}
        
        # Check if user is listed as admin for this list (grants full permissions)
        list_admins = list_info.get("admins", [])
        if email.lower() in [admin.lower() for admin in list_admins]:
            return {"has_permission": True, "message": "User has admin permission for list"}
        
        # Check if user exists in permissions collection
        user_permission = db.noteslist_permissions.find_one({"email": email.lower()})
        
        if not user_permission:
            return {"has_permission": False, "message": "User not found in permissions database"}
        
        # Check if user has view permission for this list
        user_lists = user_permission.get("lists", {})
        list_permission = user_lists.get(list_id, {})
        
        if not list_permission.get("can_view", False):
            return {"has_permission": False, "message": f"User does not have view permission for list ID '{list_id}'"}
        
        return {"has_permission": True, "message": "User has permission to view notes"}
        
    except errors.PyMongoError as e:
        logger.error(f"Database error while checking permissions for {email}: {e}")
        return {"has_permission": False, "message": "Database error while checking permissions"}
    except Exception as e:
        logger.error(f"Unexpected error while checking permissions for {email}: {e}")
        return {"has_permission": False, "message": "Unexpected error while checking permissions"}


def get_notes_from_list(email: str, list_id: str, page: int = 1, page_size: int = 20, sort_by: str = None) -> Dict[str, Any]:
    """Get all notes from a specific list that the user has permission to view.
    
    Args:
        email: The email of the authenticated user
        list_id: The ID of the list to retrieve notes from
        page: Page number for pagination (1-based)
        page_size: Number of items per page
        sort_by: Optional sorting method (e.g., 'priority' for priority-based sorting)
        
    Returns:
        dict: Contains notes array and pagination metadata
        
    Raises:
        ValueError: If user doesn't have permission or list doesn't exist
        Exception: For database errors
    """
    try:
        db = get_notes_database()
        
        # Validate pagination parameters
        if page < 1:
            raise ValueError("Page must be greater than 0")
        if page_size < 1 or page_size > 100:
            raise ValueError("Page size must be between 1 and 100")
        
        # Check user permissions
        permission_result = check_user_list_view_permission(email, list_id)
        
        if not permission_result["has_permission"]:
            raise ValueError(permission_result["message"])
        
        # Get notes from note_items collection for this list
        notes_query = {"list_id": list_id}
        
        # Calculate pagination
        skip_count = (page - 1) * page_size
        
        # Get total count first
        total_count = db.note_items.count_documents(notes_query)
        
        # Get paginated notes with optional sorting
        if sort_by == 'priority':
            # Use aggregation pipeline for proper priority sorting
            # Priority order: high (3) -> medium (2) -> low (1)
            pipeline = [
                {"$match": notes_query},
                {"$addFields": {
                    "priority_order": {
                        "$switch": {
                            "branches": [
                                {"case": {"$eq": ["$priority", "high"]}, "then": 3},
                                {"case": {"$eq": ["$priority", "medium"]}, "then": 2},
                                {"case": {"$eq": ["$priority", "low"]}, "then": 1}
                            ],
                            "default": 2
                        }
                    }
                }},
                {"$sort": {"priority_order": -1, "created_at": -1}},
                {"$skip": skip_count},
                {"$limit": page_size}
            ]
            notes_cursor = db.note_items.aggregate(pipeline)
        else:
            # Default: no specific sorting (maintain insertion order)
            notes_cursor = db.note_items.find(notes_query).skip(skip_count).limit(page_size)
        
        # Convert MongoDB documents to list format
        notes_data = []
        for note_doc in notes_cursor:
            # Convert ObjectId to string for response
            note_info = {
                "note_id": str(note_doc["_id"]),
                "title": note_doc.get("title", ""),
                "description": note_doc.get("description", ""),
                "priority": note_doc.get("priority", "medium"),
                "author_name": note_doc.get("author_name", ""),
                "author_email": note_doc.get("author_email", ""),
                "list_id": note_doc.get("list_id", ""),
                "column": note_doc.get("column", "todo"),  # Add column field with default
                "created_at": str(note_doc.get("created_at")) if note_doc.get("created_at") else None,
                "updated_at": str(note_doc.get("updated_at")) if note_doc.get("updated_at") else None
            }
            notes_data.append(note_info)
        
        total_pages = (total_count + page_size - 1) // page_size
        
        logger.info(f"Retrieved {len(notes_data)} notes for list {list_id} by user {email} (page {page}/{total_pages})")
        
        return {
            "notes": notes_data,
            "total_count": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
        
    except ValueError:
        # Re-raise ValueError (validation errors)
        raise
    except errors.PyMongoError as e:
        logger.error(f"Database error while getting notes for list {list_id}: {e}")
        raise Exception(f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in get_notes_from_list: {e}")
        raise Exception(f"Failed to retrieve notes: {str(e)}")


def get_notes(email: str, password: str, list_id: str, page: int = 1, page_size: int = 20, sort_by: str = None) -> Dict[str, Any]:
    """Get notes for a user with authentication check.
    
    Args:
        email: The email of the authenticated user
        password: The password for authentication
        list_id: The ID of the list to retrieve notes from
        page: Page number for pagination (1-based)
        page_size: Number of items per page
        sort_by: Optional sorting method (e.g., 'priority' for priority-based sorting)
        
    Returns:
        dict: Contains notes array and pagination metadata
        
    Raises:
        ValueError: If authentication fails or user not found
        Exception: For database errors
    """
    try:
        # Get notes from the specified list
        result = get_notes_from_list(email, list_id, page, page_size, sort_by)
        
        return result
        
    except ValueError:
        # Re-raise ValueError (validation errors)
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_notes: {e}")
        raise Exception(f"Failed to get notes: {str(e)}")
