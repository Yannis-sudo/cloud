"""Note management functionality."""

import logging
from typing import Dict, Any, Optional
from pymongo import errors
from pymongo.results import InsertOneResult

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


def init_notes_collections():
    """Initialize notes database collections and indexes."""
    try:
        db = get_notes_database()
        
        # Create collections if they don't exist
        noteslist_permissions = db.noteslist_permissions
        lists = db.lists
        
        # Create indexes
        try:
            noteslist_permissions.create_index("email", unique=True)
            logger.info("Created unique index on noteslist_permissions.email")
        except errors.OperationFailure as e:
            if "already exists" not in str(e):
                logger.warning(f"Index creation warning for noteslist_permissions.email: {e}")
        
        try:
            lists.create_index([("list_name", 1), ("author_email", 1)])
            logger.info("Created composite index on lists.list_name and lists.author_email")
        except errors.OperationFailure as e:
            if "already exists" not in str(e):
                logger.warning(f"Index creation warning for lists: {e}")
        
        return db
    except Exception as e:
        logger.error(f"Notes database initialization failed: {e}")
        raise


def check_user_permission(email: str, list_name: str) -> Dict[str, Any]:
    """Check if user has permission to create notes in the specified list.
    
    Args:
        email: The email address of the user
        list_name: The name of the list to check permissions for
        
    Returns:
        Dict containing permission status and details
    """
    try:
        db = get_notes_database()
        
        # Check if list exists and get list information
        list_info = db.lists.find_one({"list_name": list_name})
        
        if not list_info:
            return {"has_permission": False, "message": f"List '{list_name}' does not exist"}
        
        # Check if user is listed as admin for this list (grants full permissions)
        list_admins = list_info.get("admins", [])
        if email.lower() in [admin.lower() for admin in list_admins]:
            return {"has_permission": True, "message": "User has admin permission for list"}
        
        # Check if user exists in permissions collection
        user_permission = db.noteslist_permissions.find_one({"email": email.lower()})
        
        if not user_permission:
            return {"has_permission": False, "message": "User not found in permissions database"}
        
        # Check if user has create permission for this list
        user_lists = user_permission.get("lists", {})
        list_permission = user_lists.get(list_name, {})
        
        if not list_permission.get("can_create", False):
            return {"has_permission": False, "message": f"User does not have create permission for list '{list_name}'"}
        
        return {"has_permission": True, "message": "User has permission to create notes"}
        
    except errors.PyMongoError as e:
        logger.error(f"Database error while checking permissions for {email}: {e}")
        return {"has_permission": False, "message": "Database error while checking permissions"}
    except Exception as e:
        logger.error(f"Unexpected error while checking permissions for {email}: {e}")
        return {"has_permission": False, "message": "Unexpected error while checking permissions"}


def add_note_to_db(title: str, description: str, priority: str, author_name: str, 
                   author_email: str, list_name: str) -> Optional[InsertOneResult]:
    """Add a note to the specified list in the database.
    
    Args:
        title: The title of the note
        description: The description/content of the note
        priority: The priority level (low, medium, high)
        author_name: The name of the note author
        author_email: The email address of the note author
        list_name: The name of the list to add the note to
        
    Returns:
        InsertOneResult if successful, None otherwise
    """
    try:
        db = get_notes_database()
        
        note_document = {
            "title": title,
            "description": description,
            "priority": priority,
            "author_name": author_name,
            "author_email": author_email.lower(),
            "list_name": list_name,
            "created_at": None,  # Will be set by MongoDB
            "updated_at": None   # Will be set by MongoDB
        }
        
        result = db.lists.insert_one(note_document)
        logger.info(f"Successfully added note '{title}' to list '{list_name}' by {author_email}")
        return result
        
    except errors.PyMongoError as e:
        logger.error(f"Database error while adding note to list '{list_name}': {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error while adding note to list '{list_name}': {e}")
        return None


def add_note(username: str, password: str, title: str, description: str, 
             priority: str, author_name: str, author_email: str, list: list):
    """Add a new note to the system with permission checking.
    
    Args:
        username: The username of the authenticated user
        password: The password of the authenticated user
        title: The title of the note
        description: The description/content of the note
        priority: The priority level (low, medium, high)
        author_name: The name of the note author
        author_email: The email address of the note author
        list: A list containing the list name (expected to be [list_name])
        
    Raises:
        ValueError: If user doesn't have permission or list doesn't exist
        Exception: For database errors
    """
    try:
        # Initialize notes collections
        init_notes_collections()
        
        # Extract list name from the list parameter
        if not list or len(list) == 0:
            raise ValueError("List name is required")
        
        list_name = list[0] if isinstance(list, list) else str(list)
        
        # Check user permissions
        permission_result = check_user_permission(author_email, list_name)
        
        if not permission_result["has_permission"]:
            raise ValueError(permission_result["message"])
        
        # Add the note to the database
        result = add_note_to_db(title, description, priority, author_name, author_email, list_name)
        
        if result is None:
            raise Exception("Failed to add note to database")
        
        logger.info(f"Note '{title}' successfully added to list '{list_name}' by {author_email}")
        
    except ValueError:
        # Re-raise ValueError (permission issues, validation errors)
        raise
    except Exception as e:
        logger.error(f"Unexpected error in add_note: {e}")
        raise Exception(f"Failed to add note: {str(e)}")
