"""Base repository with common database operations."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Generic, TypeVar
from datetime import datetime
from bson import ObjectId
from pymongo import errors
from pymongo.collection import Collection
from pymongo.database import Database

from app.database.connection import get_database, get_transaction
from app.core.exceptions import DatabaseError, NotFoundError, ConflictError

logger = logging.getLogger(__name__)

T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    """Base repository with common database operations."""
    
    def __init__(self, collection_name: str):
        """Initialize repository with collection name.
        
        Args:
            collection_name: Name of the MongoDB collection
        """
        self.collection_name = collection_name
        self._collection: Optional[Collection] = None
    
    @property
    def collection(self) -> Collection:
        """Get MongoDB collection instance.
        
        Returns:
            Collection: MongoDB collection
        """
        if self._collection is None:
            db = get_database()
            self._collection = db[self.collection_name]
        return self._collection
    
    def _prepare_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare document for database insertion.
        
        Args:
            document: Document to prepare
            
        Returns:
            Dict[str, Any]: Prepared document
        """
        # Add timestamps
        now = datetime.utcnow()
        document["created_at"] = now
        document["updated_at"] = now
        
        # Convert string IDs to ObjectId if needed
        if "_id" in document and isinstance(document["_id"], str):
            document["_id"] = ObjectId(document["_id"])
            
        return document
    
    def _serialize_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize document for API response.
        
        Args:
            document: Document to serialize
            
        Returns:
            Dict[str, Any]: Serialized document
        """
        if document and "_id" in document:
            document["_id"] = str(document["_id"])
            
        return document
    
    async def create(self, document: Dict[str, Any]) -> str:
        """Create a new document.
        
        Args:
            document: Document data
            
        Returns:
            str: ID of the created document
            
        Raises:
            DatabaseError: If creation fails
            ConflictError: If document already exists
        """
        try:
            prepared_doc = self._prepare_document(document.copy())
            result = self.collection.insert_one(prepared_doc)
            
            logger.info(f"Created document in {self.collection_name} with ID: {result.inserted_id}")
            return str(result.inserted_id)
            
        except errors.DuplicateKeyError as e:
            logger.warning(f"Duplicate document in {self.collection_name}: {e}")
            raise ConflictError(f"Document already exists: {e}")
        except errors.PyMongoError as e:
            logger.error(f"Error creating document in {self.collection_name}: {e}")
            raise DatabaseError(f"Failed to create document: {e}")
    
    async def get_by_id(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get document by ID.
        
        Args:
            document_id: Document ID
            
        Returns:
            Optional[Dict[str, Any]]: Document data or None if not found
            
        Raises:
            DatabaseError: If operation fails
        """
        try:
            object_id = ObjectId(document_id)
            document = self.collection.find_one({"_id": object_id})
            
            if document:
                return self._serialize_document(document)
            return None
            
        except errors.InvalidId as e:
            logger.error(f"Invalid ID format in {self.collection_name}: {document_id}")
            raise DatabaseError(f"Invalid ID format: {e}")
        except errors.PyMongoError as e:
            logger.error(f"Error getting document from {self.collection_name}: {e}")
            raise DatabaseError(f"Failed to get document: {e}")
    
    async def get_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get one document by query.
        
        Args:
            query: Query criteria
            
        Returns:
            Optional[Dict[str, Any]]: Document data or None if not found
            
        Raises:
            DatabaseError: If operation fails
        """
        try:
            document = self.collection.find_one(query)
            
            if document:
                return self._serialize_document(document)
            return None
            
        except errors.PyMongoError as e:
            logger.error(f"Error getting document from {self.collection_name}: {e}")
            raise DatabaseError(f"Failed to get document: {e}")
    
    async def get_many(
        self,
        query: Dict[str, Any] = None,
        sort: List[tuple] = None,
        limit: int = None,
        skip: int = None
    ) -> List[Dict[str, Any]]:
        """Get multiple documents by query.
        
        Args:
            query: Query criteria
            sort: Sort specification
            limit: Number of documents to return
            skip: Number of documents to skip
            
        Returns:
            List[Dict[str, Any]]: List of documents
            
        Raises:
            DatabaseError: If operation fails
        """
        try:
            cursor = self.collection.find(query or {})
            
            if sort:
                cursor = cursor.sort(sort)
            if skip:
                cursor = cursor.skip(skip)
            if limit:
                cursor = cursor.limit(limit)
            
            documents = list(cursor)
            return [self._serialize_document(doc) for doc in documents]
            
        except errors.PyMongoError as e:
            logger.error(f"Error getting documents from {self.collection_name}: {e}")
            raise DatabaseError(f"Failed to get documents: {e}")
    
    async def update(self, document_id: str, update_data: Dict[str, Any]) -> bool:
        """Update a document.
        
        Args:
            document_id: Document ID
            update_data: Data to update
            
        Returns:
            bool: True if updated successfully, False if not found
            
        Raises:
            DatabaseError: If operation fails
        """
        try:
            object_id = ObjectId(document_id)
            update_data["updated_at"] = datetime.utcnow()
            
            result = self.collection.update_one(
                {"_id": object_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                logger.info(f"Updated document in {self.collection_name} with ID: {document_id}")
                return True
            return False
            
        except errors.InvalidId as e:
            logger.error(f"Invalid ID format in {self.collection_name}: {document_id}")
            raise DatabaseError(f"Invalid ID format: {e}")
        except errors.PyMongoError as e:
            logger.error(f"Error updating document in {self.collection_name}: {e}")
            raise DatabaseError(f"Failed to update document: {e}")
    
    async def delete(self, document_id: str) -> bool:
        """Delete a document.
        
        Args:
            document_id: Document ID
            
        Returns:
            bool: True if deleted successfully, False if not found
            
        Raises:
            DatabaseError: If operation fails
        """
        try:
            object_id = ObjectId(document_id)
            result = self.collection.delete_one({"_id": object_id})
            
            if result.deleted_count > 0:
                logger.info(f"Deleted document from {self.collection_name} with ID: {document_id}")
                return True
            return False
            
        except errors.InvalidId as e:
            logger.error(f"Invalid ID format in {self.collection_name}: {document_id}")
            raise DatabaseError(f"Invalid ID format: {e}")
        except errors.PyMongoError as e:
            logger.error(f"Error deleting document from {self.collection_name}: {e}")
            raise DatabaseError(f"Failed to delete document: {e}")
    
    async def count(self, query: Dict[str, Any] = None) -> int:
        """Count documents matching query.
        
        Args:
            query: Query criteria
            
        Returns:
            int: Number of matching documents
            
        Raises:
            DatabaseError: If operation fails
        """
        try:
            return self.collection.count_documents(query or {})
        except errors.PyMongoError as e:
            logger.error(f"Error counting documents in {self.collection_name}: {e}")
            raise DatabaseError(f"Failed to count documents: {e}")
    
    async def exists(self, query: Dict[str, Any]) -> bool:
        """Check if document exists.
        
        Args:
            query: Query criteria
            
        Returns:
            bool: True if document exists, False otherwise
            
        Raises:
            DatabaseError: If operation fails
        """
        try:
            return self.collection.count_documents(query, limit=1) > 0
        except errors.PyMongoError as e:
            logger.error(f"Error checking document existence in {self.collection_name}: {e}")
            raise DatabaseError(f"Failed to check document existence: {e}")
    
    async def create_index(self, index_spec: List[tuple], unique: bool = False) -> None:
        """Create index on collection.
        
        Args:
            index_spec: Index specification
            unique: Whether index should be unique
            
        Raises:
            DatabaseError: If index creation fails
        """
        try:
            self.collection.create_index(index_spec, unique=unique)
            logger.info(f"Created index on {self.collection_name}: {index_spec}")
        except errors.OperationFailure as e:
            if "already exists" not in str(e):
                logger.warning(f"Index creation warning for {self.collection_name}: {e}")
        except Exception as e:
            logger.error(f"Error creating index on {self.collection_name}: {e}")
            raise DatabaseError(f"Index creation error: {e}")
    
    @abstractmethod
    def get_model_schema(self) -> Dict[str, Any]:
        """Get the model schema for validation.
        
        Returns:
            Dict[str, Any]: Model schema
        """
        pass
