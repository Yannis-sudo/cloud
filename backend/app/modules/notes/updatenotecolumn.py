"""Note column update functionality."""

import logging
from typing import Dict, Any, Optional
from pymongo import errors
from pymongo.results import UpdateResult

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
        note_items = db.note_items
        
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
        
        try:
            # Create indexes for note_items collection
            note_items.create_index("list_id")
            logger.info("Created index on note_items.list_id")
        except errors.OperationFailure as e:
            if "already exists" not in str(e):
                logger.warning(f"Index creation warning for note_items.list_id: {e}")
        
        try:
            note_items.create_index("author_email")
            logger.info("Created index on note_items.author_email")
        except errors.OperationFailure as e:
            if "already exists" not in str(e):
                logger.warning(f"Index creation warning for note_items.author_email: {e}")
        
        return db
    except Exception as e:
        logger.error(f"Notes database initialization failed: {e}")
        raise


def check_user_edit_permission(email: str, list_id: str) -> Dict[str, Any]:
    """Check if user has both can_view and can_edit permissions for the specified list by ID.
    
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
            from bson import ObjectId
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
        
        # Check if user has both can_view and can_edit permission for this list
        user_lists = user_permission.get("lists", {})
        list_permission = user_lists.get(list_id, {})
        
        if not list_permission.get("can_view", False):
            return {"has_permission": False, "message": f"User does not have view permission for list ID '{list_id}'"}
        
        if not list_permission.get("can_edit", False):
            return {"has_permission": False, "message": f"User does not have edit permission for list ID '{list_id}'"}
        
        return {"has_permission": True, "message": "User has view and edit permissions"}
        
    except errors.PyMongoError as e:
        logger.error(f"Database error while checking permissions for {email}: {e}")
        return {"has_permission": False, "message": "Database error while checking permissions"}
    except Exception as e:
        logger.error(f"Unexpected error while checking permissions for {email}: {e}")
        return {"has_permission": False, "message": "Unexpected error while checking permissions"}


def update_note_column_in_db(note_id: str, new_column: str) -> Optional[UpdateResult]:
    """Update the column of a note in the database.
    
    Args:
        note_id: The ObjectId of the note to update
        new_column: The new column value (backlog, todo, in-progress, done)
        
    Returns:
        UpdateResult if successful, None otherwise
    """
    try:
        db = get_notes_database()
        
        # Validate note_id format
        try:
            from bson import ObjectId
            object_id = ObjectId(note_id)
        except:
            logger.error(f"Invalid note_id format: {note_id}")
            return None
        
        # Update the note's column
        result = db.note_items.update_one(
            {"_id": object_id},
            {"$set": {"column": new_column}}
        )
        
        if result.matched_count == 0:
            logger.warning(f"No note found with ID: {note_id}")
            return None
        
        if result.modified_count == 0:
            logger.warning(f"Note {note_id} column was not updated (may already be {new_column})")
        
        logger.info(f"Successfully updated note '{note_id}' column to '{new_column}'")
        return result
        
    except errors.PyMongoError as e:
        logger.error(f"Database error while updating note column for {note_id}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error while updating note column for {note_id}: {e}")
        return None


def update_note_column(username: str, password: str, note_id: str, new_column: str):
    """Update the column of an existing note with permission checking.
    
    Args:
        username: The username of the authenticated user
        password: The password of the authenticated user
        note_id: The ObjectId of the note to update
        new_column: The new column value (backlog, todo, in-progress, done)
        
    Raises:
        ValueError: If user doesn't have permission or note doesn't exist
        Exception: For database errors
    """
    try:
        # Initialize notes collections
        init_notes_collections()
        
        # First, get the note to find which list it belongs to
        db = get_notes_database()
        
        # Validate note_id format and get note info
        try:
            from bson import ObjectId
            object_id = ObjectId(note_id)
            note = db.note_items.find_one({"_id": object_id})
        except:
            raise ValueError(f"Invalid note ID format: {note_id}")
        
        if not note:
            raise ValueError(f"Note with ID '{note_id}' does not exist")
        
        # Get the list_id from the note
        list_id = note.get("list_id")
        if not list_id:
            raise ValueError("Note does not have an associated list_id")
        
        # Check user permissions for the list
        permission_result = check_user_edit_permission(username, list_id)
        
        if not permission_result["has_permission"]:
            raise ValueError(permission_result["message"])
        
        # Update the note's column in the database
        result = update_note_column_in_db(note_id, new_column)
        
        if result is None:
            raise Exception("Failed to update note column in database")
        
        logger.info(f"Note '{note_id}' column successfully updated to '{new_column}' by {username}")
        
    except ValueError:
        # Re-raise ValueError (permission issues, validation errors)
        raise
    except Exception as e:
        logger.error(f"Unexpected error in update_note_column: {e}")
        raise Exception(f"Failed to update note column: {str(e)}")
