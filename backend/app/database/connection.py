"""MongoDB database connection management."""

import logging
from typing import Optional
from pymongo import MongoClient, errors
from pymongo.database import Database
from pymongo.collection import Collection
from gridfs import GridFS
from contextlib import contextmanager

from app.config import get_settings
from app.core.exceptions import DatabaseError

logger = logging.getLogger(__name__)

settings = get_settings()
_mongo_client: Optional[MongoClient] = None


def get_mongo_client() -> MongoClient:
    """Get or create a single MongoDB client instance.
    
    Returns:
        MongoClient: MongoDB client instance
        
    Raises:
        DatabaseError: If connection fails
    """
    global _mongo_client
    
    if _mongo_client is None:
        try:
            _mongo_client = MongoClient(
                settings.DATABASE_URL,
                serverSelectionTimeoutMS=5000,
                maxPoolSize=50,  # Connection pooling
                retryWrites=True,
                w="majority",
                connectTimeoutMS=10000,
                socketTimeoutMS=30000,
            )
            
            # Test connection
            _mongo_client.admin.command("ping")
            logger.info("MongoDB connection established successfully")
            
        except errors.ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise DatabaseError(f"Database connection failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error connecting to MongoDB: {e}")
            raise DatabaseError(f"Unexpected database error: {e}")
    
    return _mongo_client


def get_database() -> Database:
    """Get the configured MongoDB database.
    
    Returns:
        Database: MongoDB database instance
        
    Raises:
        DatabaseError: If database access fails
    """
    try:
        client = get_mongo_client()
        return client[settings.DATABASE_NAME]
    except errors.ConfigurationError as e:
        logger.error(f"Database configuration error: {e}")
        raise DatabaseError(f"Database configuration error: {e}")
    except Exception as e:
        logger.error(f"Error accessing database: {e}")
        raise DatabaseError(f"Database access error: {e}")


def get_gridfs() -> GridFS:
    """Get GridFS instance for file storage.
    
    Returns:
        GridFS: GridFS instance
        
    Raises:
        DatabaseError: If GridFS access fails
    """
    try:
        db = get_database()
        return GridFS(db)
    except Exception as e:
        logger.error(f"Error accessing GridFS: {e}")
        raise DatabaseError(f"GridFS access error: {e}")


@contextmanager
def get_transaction():
    """Context manager for database transactions.
    
    Yields:
        ClientSession: MongoDB session for transactions
    """
    client = get_mongo_client()
    session = None
    
    try:
        session = client.start_session()
        session.start_transaction()
        yield session
        session.commit_transaction()
    except Exception as e:
        if session:
            session.abort_transaction()
        logger.error(f"Transaction failed: {e}")
        raise DatabaseError(f"Transaction error: {e}")
    finally:
        if session:
            session.end_session()


def close_connection():
    """Close the MongoDB connection (for cleanup)."""
    global _mongo_client
    
    if _mongo_client is not None:
        try:
            _mongo_client.close()
            _mongo_client = None
            logger.info("MongoDB connection closed")
        except Exception as e:
            logger.error(f"Error closing MongoDB connection: {e}")


def health_check() -> bool:
    """Check database health.
    
    Returns:
        bool: True if database is healthy, False otherwise
    """
    try:
        client = get_mongo_client()
        client.admin.command("ping")
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


def get_collection_stats(collection_name: str) -> dict:
    """Get collection statistics.
    
    Args:
        collection_name: Name of the collection
        
    Returns:
        dict: Collection statistics
        
    Raises:
        DatabaseError: If operation fails
    """
    try:
        db = get_database()
        collection = db[collection_name]
        
        stats = {
            "name": collection_name,
            "count": collection.count_documents({}),
            "size": 0,  # Will be populated if available
            "indexes": list(collection.list_indexes())
        }
        
        # Try to get collection size (may not be available in all MongoDB versions)
        try:
            stats["size"] = db.command("collstats", collection_name).get("size", 0)
        except Exception:
            pass  # Size information not available
            
        return stats
        
    except Exception as e:
        logger.error(f"Error getting collection stats for {collection_name}: {e}")
        raise DatabaseError(f"Collection stats error: {e}")


def create_index(collection_name: str, index_spec: list, unique: bool = False) -> None:
    """Create an index on a collection.
    
    Args:
        collection_name: Name of the collection
        index_spec: Index specification
        unique: Whether the index should be unique
        
    Raises:
        DatabaseError: If index creation fails
    """
    try:
        db = get_database()
        collection = db[collection_name]
        
        collection.create_index(index_spec, unique=unique)
        logger.info(f"Created index on {collection_name}: {index_spec}")
        
    except errors.OperationFailure as e:
        if "already exists" not in str(e):
            logger.warning(f"Index creation warning for {collection_name}: {e}")
    except Exception as e:
        logger.error(f"Error creating index on {collection_name}: {e}")
        raise DatabaseError(f"Index creation error: {e}")


def drop_index(collection_name: str, index_name: str) -> None:
    """Drop an index from a collection.
    
    Args:
        collection_name: Name of the collection
        index_name: Name of the index to drop
        
    Raises:
        DatabaseError: If index drop fails
    """
    try:
        db = get_database()
        collection = db[collection_name]
        
        collection.drop_index(index_name)
        logger.info(f"Dropped index {index_name} from {collection_name}")
        
    except Exception as e:
        logger.error(f"Error dropping index {index_name} from {collection_name}: {e}")
        raise DatabaseError(f"Index drop error: {e}")
