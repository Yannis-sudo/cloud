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


def check_user_permission(email: str, list_id: str) -> Dict[str, Any]:
    """Check if user has permission to create notes in the specified list by ID.
    
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
        
        # Check if user has create permission for this list
        user_lists = user_permission.get("lists", {})
        list_permission = user_lists.get(list_id, {})
        
        if not list_permission.get("can_create", False):
            return {"has_permission": False, "message": f"User does not have create permission for list ID '{list_id}'"}
        
        return {"has_permission": True, "message": "User has permission to create notes"}
        
    except errors.PyMongoError as e:
        logger.error(f"Database error while checking permissions for {email}: {e}")
        return {"has_permission": False, "message": "Database error while checking permissions"}
    except Exception as e:
        logger.error(f"Unexpected error while checking permissions for {email}: {e}")
        return {"has_permission": False, "message": "Unexpected error while checking permissions"}


def add_note_to_db(title: str, description: str, priority: str, author_name: str, 
                   author_email: str, list_id: str) -> Optional[InsertOneResult]:
    """Add a note to the specified list in the database using list_id.
    
    Args:
        title: The title of the note
        description: The description/content of the note
        priority: The priority level (low, medium, high)
        author_name: The name of the note author
        author_email: The email address of the note author
        list_id: The ObjectId of the list to add the note to
        
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
            "list_id": list_id,  # Use list_id instead of list_name
            "created_at": None,  # Will be set by MongoDB
            "updated_at": None   # Will be set by MongoDB
        }
        
        result = db.note_items.insert_one(note_document)
        logger.info(f"Successfully added note '{title}' to list ID '{list_id}' by {author_email}")
        return result
        
    except errors.PyMongoError as e:
        logger.error(f"Database error while adding note to list ID '{list_id}': {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error while adding note to list ID '{list_id}': {e}")
        return None


def add_note(username: str, password: str, title: str, description: str, 
             priority: str, author_name: str, author_email: str, list_id: str):
    """Add a new note to the system with permission checking using list_id.
    
    Args:
        username: The username of the authenticated user
        password: The password of the authenticated user
        title: The title of the note
        description: The description/content of the note
        priority: The priority level (low, medium, high)
        author_name: The name of the note author
        author_email: The email address of the note author
        list_id: The ObjectId of the list to add the note to
        
    Raises:
        ValueError: If user doesn't have permission or list doesn't exist
        Exception: For database errors
    """
    try:
        # Initialize notes collections
        init_notes_collections()
        
        # Check user permissions
        permission_result = check_user_permission(author_email, list_id)
        
        if not permission_result["has_permission"]:
            raise ValueError(permission_result["message"])
        
        # Add the note to the database
        result = add_note_to_db(title, description, priority, author_name, author_email, list_id)
        
        if result is None:
            raise Exception("Failed to add note to database")
        
        logger.info(f"Note '{title}' successfully added to list ID '{list_id}' by {author_email}")
        
    except ValueError:
        # Re-raise ValueError (permission issues, validation errors)
        raise
    except Exception as e:
        logger.error(f"Unexpected error in add_note: {e}")
        raise Exception(f"Failed to add note: {str(e)}")


def rollback_notes_to_lists_collection():
    """Rollback function to move notes from note_items back to lists collection.
    
    This is a safety mechanism in case the separation needs to be reverted.
    
    Returns:
        dict: Contains rollback statistics and status
    """
    try:
        db = get_notes_database()
        
        # Count notes in note_items before rollback
        notes_count_before = db.note_items.count_documents({})
        
        if notes_count_before == 0:
            return {
                "success": True,
                "message": "No notes to rollback",
                "notes_moved": 0,
                "notes_count_before": 0,
                "notes_count_after": 0
            }
        
        # Get all notes from note_items collection
        notes_to_move = list(db.note_items.find({}))
        
        moved_count = 0
        errors = []
        
        for note in notes_to_move:
            try:
                # Insert note into lists collection
                result = db.lists.insert_one(note)
                if result.inserted_id:
                    moved_count += 1
                    
                    # Remove from note_items after successful insertion
                    db.note_items.delete_one({"_id": note["_id"]})
                    
            except Exception as e:
                error_msg = f"Failed to move note {note.get('_id')}: {e}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        # Verify rollback
        notes_count_after = db.note_items.count_documents({})
        
        logger.info(f"Rollback completed: {moved_count}/{notes_count_before} notes moved back to lists collection")
        
        if errors:
            logger.warning(f"Rollback completed with {len(errors)} errors")
        
        return {
            "success": len(errors) == 0,
            "message": f"Rollback completed. Moved {moved_count} notes back to lists collection.",
            "notes_moved": moved_count,
            "notes_count_before": notes_count_before,
            "notes_count_after": notes_count_after,
            "errors": errors
        }
        
    except Exception as e:
        logger.error(f"Critical error during rollback: {e}")
        return {
            "success": False,
            "message": f"Rollback failed: {str(e)}",
            "notes_moved": 0,
            "notes_count_before": 0,
            "notes_count_after": 0,
            "errors": [str(e)]
        }
