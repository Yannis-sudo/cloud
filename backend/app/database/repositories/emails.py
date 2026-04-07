"""Email repository for database operations."""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.database.repositories.base import BaseRepository
from app.core.exceptions import DatabaseError, NotFoundError

logger = logging.getLogger(__name__)


class EmailRepository(BaseRepository):
    """Repository for email configuration and operations."""
    
    def __init__(self):
        """Initialize email repository."""
        super().__init__("email_addresses")
    
    async def add_email_server_config(
        self,
        user_email: str,
        email: str,
        imap_server: str,
        smtp_server: str,
        imap_port: int,
        smtp_port: int,
        password: str
    ) -> str:
        """Add email server configuration.
        
        Args:
            user_email: User's email (owner of this configuration)
            email: Email address to configure
            imap_server: IMAP server address
            smtp_server: SMTP server address
            imap_port: IMAP port
            smtp_port: SMTP port
            password: Email password
            
        Returns:
            str: ID of the created configuration
            
        Raises:
            DatabaseError: If creation fails
        """
        email_data = {
            "user_email": user_email.lower(),
            "email": email.lower(),
            "server_incoming": imap_server,
            "server_outgoing": smtp_server,
            "server_incoming_port": imap_port,
            "server_outgoing_port": smtp_port,
            "password": password,
            "is_active": True,
            "last_sync": None
        }
        
        return await self.create(email_data)
    
    async def get_user_emails(self, user_email: str) -> List[Dict[str, Any]]:
        """Get all email configurations for a user.
        
        Args:
            user_email: User's email
            
        Returns:
            List[Dict[str, Any]]: List of email configurations
        """
        return await self.get_many({"user_email": user_email.lower()})
    
    async def get_email_config(self, email: str) -> Optional[Dict[str, Any]]:
        """Get email configuration by email address.
        
        Args:
            email: Email address
            
        Returns:
            Optional[Dict[str, Any]]: Email configuration or None
        """
        return await self.get_one({"email": email.lower()})
    
    async def update_email_password(self, email_id: str, new_password: str) -> bool:
        """Update email password.
        
        Args:
            email_id: Email configuration ID
            new_password: New password
            
        Returns:
            bool: True if updated successfully
        """
        return await self.update(email_id, {"password": new_password})
    
    async def update_last_sync(self, email_id: str) -> bool:
        """Update last sync timestamp.
        
        Args:
            email_id: Email configuration ID
            
        Returns:
            bool: True if updated successfully
        """
        return await self.update(email_id, {"last_sync": datetime.utcnow()})
    
    async def deactivate_email_config(self, email_id: str) -> bool:
        """Deactivate email configuration.
        
        Args:
            email_id: Email configuration ID
            
        Returns:
            bool: True if deactivated successfully
        """
        return await self.update(email_id, {"is_active": False})
    
    async def activate_email_config(self, email_id: str) -> bool:
        """Activate email configuration.
        
        Args:
            email_id: Email configuration ID
            
        Returns:
            bool: True if activated successfully
        """
        return await self.update(email_id, {"is_active": True})
    
    async def delete_email_config(self, email_id: str) -> bool:
        """Delete email configuration.
        
        Args:
            email_id: Email configuration ID
            
        Returns:
            bool: True if deleted successfully
        """
        return await self.delete(email_id)
    
    async def get_active_email_configs(self, user_email: str) -> List[Dict[str, Any]]:
        """Get active email configurations for a user.
        
        Args:
            user_email: User's email
            
        Returns:
            List[Dict[str, Any]]: List of active email configurations
        """
        return await self.get_many({
            "user_email": user_email.lower(),
            "is_active": True
        })
    
    async def update_sync_status(
        self,
        email_id: str,
        status: str,
        error_message: Optional[str] = None
    ) -> bool:
        """Update email sync status.
        
        Args:
            email_id: Email configuration ID
            status: Sync status
            error_message: Optional error message
            
        Returns:
            bool: True if updated successfully
        """
        update_data = {
            "sync_status": status,
            "last_sync_attempt": datetime.utcnow()
        }
        
        if error_message:
            update_data["last_sync_error"] = error_message
        
        return await self.update(email_id, update_data)
    
    async def get_email_stats(self, user_email: str) -> Dict[str, Any]:
        """Get email statistics for a user.
        
        Args:
            user_email: User's email
            
        Returns:
            Dict[str, Any]: Email statistics
        """
        try:
            configs = await self.get_user_emails(user_email)
            
            stats = {
                "total_configs": len(configs),
                "active_configs": len([c for c in configs if c.get("is_active", True)]),
                "last_sync": None,
                "sync_errors": 0
            }
            
            # Find the most recent sync
            for config in configs:
                if config.get("last_sync"):
                    if stats["last_sync"] is None or config["last_sync"] > stats["last_sync"]:
                        stats["last_sync"] = config["last_sync"]
                
                if config.get("sync_status") == "error":
                    stats["sync_errors"] += 1
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting email stats for {user_email}: {e}")
            return {}
    
    def get_model_schema(self) -> Dict[str, Any]:
        """Get email model schema.
        
        Returns:
            Dict[str, Any]: Email model schema
        """
        return {
            "type": "object",
            "properties": {
                "user_email": {"type": "string", "format": "email"},
                "email": {"type": "string", "format": "email"},
                "server_incoming": {"type": "string"},
                "server_outgoing": {"type": "string"},
                "server_incoming_port": {"type": "integer", "minimum": 1, "maximum": 65535},
                "server_outgoing_port": {"type": "integer", "minimum": 1, "maximum": 65535},
                "password": {"type": "string"},
                "is_active": {"type": "boolean", "default": True},
                "last_sync": {"type": "string", "format": "date-time"},
                "sync_status": {"type": "string", "enum": ["success", "error", "pending"]},
                "last_sync_error": {"type": "string"}
            },
            "required": ["user_email", "email", "server_incoming", "server_outgoing", 
                        "server_incoming_port", "server_outgoing_port", "password"],
            "additionalProperties": False
        }
