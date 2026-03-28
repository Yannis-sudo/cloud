"""MongoDB database access layer."""

import logging
from typing import List, Union, Dict, Any
from pymongo import MongoClient, errors
from pymongo.collection import Collection
from pymongo.results import InsertOneResult
from bson import ObjectId

from app.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()
_mongo_client: MongoClient | None = None


def get_mongo_client() -> MongoClient:
    """Get or create a single MongoDB client instance."""
    global _mongo_client
    if _mongo_client is None:
        try:
            _mongo_client = MongoClient(
                settings.DATABASE_URL, 
                serverSelectionTimeoutMS=5000,
                maxPoolSize=50,  # Connection pooling
                retryWrites=True,
                w="majority"
            )
            # Test connection
            _mongo_client.admin.command("ping")
            logger.info("MongoDB connection established successfully")
        except errors.ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error connecting to MongoDB: {e}")
            raise
    return _mongo_client


def get_database():
    """Get the configured MongoDB database."""
    try:
        return get_mongo_client()[settings.DATABASE_NAME]
    except errors.ConfigurationError as e:
        logger.error(f"Database configuration error: {e}")
        raise
    except Exception as e:
        logger.error(f"Error accessing database: {e}")
        raise


def init_db():
    """Initialize MongoDB collections and indexes (idempotent)."""
    try:
        db = get_database()
        users = db.users
        email_addresses = db.email_addresses
        
        # Create indexes only if they don't exist
        try:
            users.create_index("email", unique=True)
            logger.info("Created unique index on users.email")
        except errors.OperationFailure as e:
            if "already exists" not in str(e):
                logger.warning(f"Index creation warning for users.email: {e}")
        
        try:
            email_addresses.create_index([("user_email", 1), ("email", 1)], unique=True)
            logger.info("Created composite unique index on email_addresses")
        except errors.OperationFailure as e:
            if "already exists" not in str(e):
                logger.warning(f"Index creation warning for email_addresses: {e}")
        
        return db
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


def get_user_emails(email: str) -> Union[str, List[Dict[str, Any]]]:
    """Get associated email records for a user by user email."""
    if not email or not isinstance(email, str):
        logger.warning("Invalid email parameter provided")
        return "Email not found"
    
    try:
        db = get_database()  # Use get_database instead of init_db for better performance
        
        # Debug: Log all documents in email_addresses collection
        all_docs = list(db.email_addresses.find({}))
        logger.info(f"All email_addresses documents: {all_docs}")
        
        # Check if there are any email records for this user
        count = db.email_addresses.count_documents({"user_email": email.lower()})
        logger.info(f"Count of documents with user_email {email.lower()}: {count}")
        
        if count == 0:
            logger.info(f"No email records found for user: {email.lower()}")
            return "Email not found"
        
        # Return the list of email records
        emails = list(db.email_addresses.find({"user_email": email.lower()}))
        logger.info(f"Found {len(emails)} email records for user: {email.lower()}")
        return emails
        
    except errors.PyMongoError as e:
        logger.error(f"Database error while fetching emails for {email}: {e}")
        return "Email not found"
    except Exception as e:
        logger.error(f"Unexpected error while fetching emails for {email}: {e}")
        return "Email not found"


def add_user_email(user_email: str, email: str, server: str, password: str) -> Union[InsertOneResult, None]:
    """Add email account for user."""
    # Input validation
    if not all([user_email, email, server, password]) or not all(isinstance(param, str) for param in [user_email, email, server, password]):
        logger.warning("Invalid parameters provided for add_user_email")
        return None
    
    try:
        db = get_database()  # Use get_database instead of init_db for better performance
        
        result = db.email_addresses.insert_one({
            "user_email": user_email.lower(), 
            "email": email.lower(), 
            "server": server, 
            "password": password
        })
        
        logger.info(f"Successfully added email {email} for user {user_email.lower()}")
        return result
        
    except errors.DuplicateKeyError as e:
        logger.warning(f"Duplicate email entry for {user_email.lower()}: {e}")
        return None
    except errors.PyMongoError as e:
        logger.error(f"Database error while adding email for {user_email}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error while adding email for {user_email}: {e}")
        return None


def add_email_server_config(imap_server: str, smtp_server: str, imap_port: int, smtp_port: int, email: str, password: str) -> bool:
    """Add email server configuration to the email_addresses collection."""
    # Input validation
    if not all([imap_server, smtp_server, email, password]) or not all(isinstance(param, str) for param in [imap_server, smtp_server, email, password]):
        logger.warning("Invalid parameters provided for add_email_server_config")
        return False
    
    if not isinstance(imap_port, int) or not isinstance(smtp_port, int):
        logger.warning("Invalid port parameters provided for add_email_server_config")
        return False
    
    try:
        db = get_database()
        
        # Check if the email already exists in email_addresses collection
        if db.email_addresses.find_one({"email": email.lower()}):
            logger.info(f"Email configuration already exists for: {email.lower()}")
            return False
        
        # Insert the new email configuration into email_addresses collection
        result = db.email_addresses.insert_one({
            "user_email": email.lower(),  # Add this field for get_user_emails to find
            "email": email.lower(),
            "server_incoming": imap_server,
            "server_outgoing": smtp_server,
            "server_incoming_port": imap_port,
            "server_outgoing_port": smtp_port,
            "password": password
        })
        
        logger.info(f"Successfully added email server configuration for {email.lower()}")
        return True
        
    except errors.DuplicateKeyError as e:
        logger.warning(f"Duplicate email configuration for {email.lower()}: {e}")
        return False
    except errors.PyMongoError as e:
        logger.error(f"Database error while adding email server config for {email}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error while adding email server config for {email}: {e}")
        return False


def close_connection():
    """Close the MongoDB connection (for cleanup)."""
    global _mongo_client
    if _mongo_client is not None:
        _mongo_client.close()
        _mongo_client = None
        logger.info("MongoDB connection closed")
