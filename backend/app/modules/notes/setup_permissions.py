"""Setup script for notes permissions and initial data."""

import logging
from pymongo import errors

from app.database import get_database, get_mongo_client

logger = logging.getLogger(__name__)


def setup_notes_permissions():
    """Set up initial notes permissions by loading users from the main database."""
    try:
        # Get both databases
        client = get_mongo_client()
        main_db = get_database()  # This gets the main "cloud" database
        notes_db = client["notes"]  # This gets the notes database
        
        # Create collections if they don't exist
        noteslist_permissions = notes_db.noteslist_permissions
        lists = notes_db.lists
        
        # Create indexes
        try:
            noteslist_permissions.create_index("email", unique=True)
            logger.info("Created unique index on noteslist_permissions.email")
        except errors.OperationFailure as e:
            if "already exists" not in str(e):
                logger.warning(f"Index creation warning: {e}")
        
        # Load all users from the main database
        users_collection = main_db.users
        all_users = list(users_collection.find({}))
        
        if not all_users:
            logger.warning("No users found in the main database. Please create users first.")
            return False
        
        logger.info(f"Found {len(all_users)} users in the main database")
        
        # Create permissions for each user
        for user in all_users:
            user_email = user.get("email", "").lower()
            username = user.get("username", "")
            
            if not user_email:
                logger.warning(f"User {username} has no email, skipping")
                continue
            
            # Determine if user should be admin based on database role field
            # Check if user has admin role in the database
            is_admin = user.get("role") == "admin" or user.get("is_admin") == True
            
            # Set up permissions based on user role
            if is_admin:
                user_permissions = {
                    "email": user_email,
                    "username": username,
                    "role": "admin",
                    "lists": {
                        "general": {
                            "can_view": True,
                            "can_create": True,
                            "can_edit": True,
                            "can_delete": True
                        },
                        "work": {
                            "can_view": True,
                            "can_create": True,
                            "can_edit": True,
                            "can_delete": True
                        },
                        "personal": {
                            "can_view": True,
                            "can_create": True,
                            "can_edit": True,
                            "can_delete": True
                        }
                    }
                }
                logger.info(f"Setting up admin permissions for {user_email}")
            else:
                # Regular users get basic permissions
                user_permissions = {
                    "email": user_email,
                    "username": username,
                    "role": "user",
                    "lists": {
                        "general": {
                            "can_view": True,
                            "can_create": True,
                            "can_edit": False,
                            "can_delete": False
                        },
                        "personal": {
                            "can_view": True,
                            "can_create": True,
                            "can_edit": True,
                            "can_delete": True
                        }
                    }
                }
                logger.info(f"Setting up user permissions for {user_email}")
            
            # Insert permissions
            try:
                noteslist_permissions.insert_one(user_permissions)
                logger.info(f"Added permissions for {user_email}")
                
            except errors.DuplicateKeyError:
                logger.info(f"Permissions already exist for {user_email}")
        
        # Create example lists with admin information
        admin_emails = [user.get("email", "").lower() for user in all_users 
                       if user.get("role") == "admin" or user.get("is_admin") == True]
        
        example_lists = [
            {
                "list_name": "general", 
                "description": "General notes list", 
                "created_by": "system",
                "admins": admin_emails
            },
            {
                "list_name": "work", 
                "description": "Work-related notes", 
                "created_by": "system",
                "admins": admin_emails
            },
            {
                "list_name": "personal", 
                "description": "Personal notes", 
                "created_by": "system",
                "admins": admin_emails
            }
        ]
        
        for list_data in example_lists:
            try:
                lists.insert_one(list_data)
                logger.info(f"Created list: {list_data['list_name']} with admins: {admin_emails}")
            except errors.DuplicateKeyError:
                # If list exists, update it with current admins
                lists.update_one(
                    {"list_name": list_data["list_name"]},
                    {"$set": {"admins": admin_emails}}
                )
                logger.info(f"Updated list '{list_data['list_name']}' with admins: {admin_emails}")
        
        logger.info("Notes permissions setup completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error setting up notes permissions: {e}")
        return False


def add_user_to_notes_permissions(user_email: str, username: str, role: str = "user"):
    """Add a specific user to notes permissions.
    
    Args:
        user_email: Email address of the user
        username: Username of the user
        role: Role of the user (admin or user)
    """
    try:
        client = get_mongo_client()
        notes_db = client["notes"]
        noteslist_permissions = notes_db.noteslist_permissions
        
        user_email = user_email.lower()
        
        if role == "admin":
            user_permissions = {
                "email": user_email,
                "username": username,
                "role": "admin",
                "lists": {
                    "general": {"can_view": True, "can_create": True, "can_edit": True, "can_delete": True},
                    "work": {"can_view": True, "can_create": True, "can_edit": True, "can_delete": True},
                    "personal": {"can_view": True, "can_create": True, "can_edit": True, "can_delete": True}
                }
            }
        else:
            user_permissions = {
                "email": user_email,
                "username": username,
                "role": "user",
                "lists": {
                    "general": {"can_view": True, "can_create": True, "can_edit": False, "can_delete": False},
                    "personal": {"can_view": True, "can_create": True, "can_edit": True, "can_delete": True}
                }
            }
        
        try:
            noteslist_permissions.insert_one(user_permissions)
            logger.info(f"Added {role} permissions for {user_email}")
            
            # If user is admin, add them to all lists as admin
            if role == "admin":
                lists = notes_db.lists
                # Add admin to all existing lists
                result = lists.update_many(
                    {},
                    {"$addToSet": {"admins": user_email}}
                )
                logger.info(f"Added {user_email} as admin to {result.modified_count} lists")
            
            return True
        except errors.DuplicateKeyError:
            logger.info(f"Permissions already exist for {user_email}")
            return False
            
    except Exception as e:
        logger.error(f"Error adding user {user_email} to notes permissions: {e}")
        return False


if __name__ == "__main__":
    setup_notes_permissions()
