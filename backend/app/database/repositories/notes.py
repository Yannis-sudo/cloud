"""Notes repository for database operations."""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.database.repositories.base import BaseRepository
from app.core.exceptions import DatabaseError, NotFoundError

logger = logging.getLogger(__name__)


class NotesRepository(BaseRepository):
    """Repository for notes and lists operations."""
    
    def __init__(self):
        """Initialize notes repository."""
        super().__init__("notes")
    
    async def create_note(
        self,
        title: str,
        description: str,
        priority: str,
        author_name: str,
        author_email: str,
        list_id: str,
        column: str,
        **kwargs
    ) -> str:
        """Create a new note.
        
        Args:
            title: Note title
            description: Note description
            priority: Note priority (low, medium, high)
            author_name: Author's name
            author_email: Author's email
            list_id: List ID
            column: Column (backlog, todo, in-progress, done)
            **kwargs: Additional note fields
            
        Returns:
            str: ID of the created note
            
        Raises:
            DatabaseError: If creation fails
        """
        note_data = {
            "title": title,
            "description": description,
            "priority": priority,
            "author_name": author_name,
            "author_email": author_email.lower(),
            "list_id": list_id,
            "column": column,
            "is_archived": False,
            "tags": [],
            **kwargs
        }
        
        return await self.create(note_data)
    
    async def create_list(
        self,
        list_name: str,
        creator_email: str,
        description: str = "",
        **kwargs
    ) -> str:
        """Create a new notes list.
        
        Args:
            list_name: List name
            creator_email: Creator's email
            description: List description
            **kwargs: Additional list fields
            
        Returns:
            str: ID of the created list
        """
        list_data = {
            "list_name": list_name,
            "creator_email": creator_email.lower(),
            "description": description,
            "is_active": True,
            "members": [creator_email.lower()],
            "permissions": {
                creator_email.lower(): ["read", "write", "admin"]
            },
            **kwargs
        }
        
        return await self.create(list_data)
    
    async def get_notes_by_list(self, list_id: str) -> List[Dict[str, Any]]:
        """Get all notes in a list.
        
        Args:
            list_id: List ID
            
        Returns:
            List[Dict[str, Any]]: List of notes
        """
        return await self.get_many({
            "list_id": list_id,
            "is_archived": False
        })
    
    async def get_notes_by_column(self, list_id: str, column: str) -> List[Dict[str, Any]]:
        """Get notes in a specific column.
        
        Args:
            list_id: List ID
            column: Column name
            
        Returns:
            List[Dict[str, Any]]: List of notes
        """
        return await self.get_many({
            "list_id": list_id,
            "column": column,
            "is_archived": False
        })
    
    async def get_user_lists(self, user_email: str) -> List[Dict[str, Any]]:
        """Get all lists for a user.
        
        Args:
            user_email: User's email
            
        Returns:
            List[Dict[str, Any]]: List of user's lists
        """
        return await self.get_many({
            "$or": [
                {"creator_email": user_email.lower()},
                {"members": user_email.lower()}
            ],
            "is_active": True
        })
    
    async def update_note_column(self, note_id: str, new_column: str) -> bool:
        """Update note column.
        
        Args:
            note_id: Note ID
            new_column: New column
            
        Returns:
            bool: True if updated successfully
        """
        return await self.update(note_id, {"column": new_column})
    
    async def update_note_priority(self, note_id: str, new_priority: str) -> bool:
        """Update note priority.
        
        Args:
            note_id: Note ID
            new_priority: New priority
            
        Returns:
            bool: True if updated successfully
        """
        return await self.update(note_id, {"priority": new_priority})
    
    async def archive_note(self, note_id: str) -> bool:
        """Archive a note.
        
        Args:
            note_id: Note ID
            
        Returns:
            bool: True if archived successfully
        """
        return await self.update(note_id, {"is_archived": True})
    
    async def delete_list(self, list_id: str) -> bool:
        """Delete a list and all its notes.
        
        Args:
            list_id: List ID
            
        Returns:
            bool: True if deleted successfully
        """
        try:
            # First, archive all notes in the list
            await self.update_many(
                {"list_id": list_id},
                {"is_archived": True}
            )
            
            # Then deactivate the list
            await self.update(list_id, {"is_active": False})
            
            return True
        except Exception as e:
            logger.error(f"Error deleting list {list_id}: {e}")
            raise DatabaseError(f"Failed to delete list: {e}")
    
    async def add_list_member(self, list_id: str, member_email: str, permissions: List[str]) -> bool:
        """Add a member to a list with permissions.
        
        Args:
            list_id: List ID
            member_email: Member's email
            permissions: List of permissions
            
        Returns:
            bool: True if added successfully
        """
        try:
            # Get the list
            list_doc = await self.get_by_id(list_id)
            if not list_doc:
                return False
            
            # Add member to members list
            members = list_doc.get("members", [])
            if member_email.lower() not in members:
                members.append(member_email.lower())
            
            # Add permissions
            permissions_dict = list_doc.get("permissions", {})
            permissions_dict[member_email.lower()] = permissions
            
            # Update the list
            await self.update(list_id, {
                "members": members,
                "permissions": permissions_dict
            })
            
            return True
        except Exception as e:
            logger.error(f"Error adding member to list {list_id}: {e}")
            raise DatabaseError(f"Failed to add member: {e}")
    
    async def remove_list_member(self, list_id: str, member_email: str) -> bool:
        """Remove a member from a list.
        
        Args:
            list_id: List ID
            member_email: Member's email
            
        Returns:
            bool: True if removed successfully
        """
        try:
            # Get the list
            list_doc = await self.get_by_id(list_id)
            if not list_doc:
                return False
            
            # Remove member from members list
            members = list_doc.get("members", [])
            if member_email.lower() in members:
                members.remove(member_email.lower())
            
            # Remove permissions
            permissions_dict = list_doc.get("permissions", {})
            permissions_dict.pop(member_email.lower(), None)
            
            # Update the list
            await self.update(list_id, {
                "members": members,
                "permissions": permissions_dict
            })
            
            return True
        except Exception as e:
            logger.error(f"Error removing member from list {list_id}: {e}")
            raise DatabaseError(f"Failed to remove member: {e}")
    
    async def get_user_permissions(self, list_id: str, user_email: str) -> List[str]:
        """Get user permissions for a list.
        
        Args:
            list_id: List ID
            user_email: User's email
            
        Returns:
            List[str]: List of permissions
        """
        try:
            list_doc = await self.get_by_id(list_id)
            if not list_doc:
                return []
            
            permissions = list_doc.get("permissions", {})
            return permissions.get(user_email.lower(), [])
        except Exception as e:
            logger.error(f"Error getting permissions for {user_email} on list {list_id}: {e}")
            return []
    
    async def update_many(self, query: Dict[str, Any], update_data: Dict[str, Any]) -> int:
        """Update multiple documents.
        
        Args:
            query: Query criteria
            update_data: Data to update
            
        Returns:
            int: Number of updated documents
        """
        try:
            update_data["updated_at"] = datetime.utcnow()
            result = self.collection.update_many(query, {"$set": update_data})
            return result.modified_count
        except Exception as e:
            logger.error(f"Error updating multiple documents: {e}")
            raise DatabaseError(f"Failed to update multiple documents: {e}")
    
    def get_model_schema(self) -> Dict[str, Any]:
        """Get notes model schema.
        
        Returns:
            Dict[str, Any]: Notes model schema
        """
        return {
            "type": "object",
            "properties": {
                "title": {"type": "string", "minLength": 1},
                "description": {"type": "string"},
                "priority": {"type": "string", "enum": ["low", "medium", "high"]},
                "author_name": {"type": "string"},
                "author_email": {"type": "string", "format": "email"},
                "list_id": {"type": "string"},
                "column": {"type": "string", "enum": ["backlog", "todo", "in-progress", "done"]},
                "is_archived": {"type": "boolean", "default": False},
                "tags": {"type": "array", "items": {"type": "string"}},
                "list_name": {"type": "string"},
                "creator_email": {"type": "string", "format": "email"},
                "description": {"type": "string"},
                "is_active": {"type": "boolean", "default": True},
                "members": {"type": "array", "items": {"type": "string"}},
                "permissions": {"type": "object"}
            },
            "additionalProperties": True
        }
