"""Files repository for GridFS operations."""

import logging
from typing import Dict, Any, Optional, BinaryIO, Union
from datetime import datetime
from bson import ObjectId
from gridfs import GridFS
from gridfs.errors import NoFile

from app.database.connection import get_gridfs, get_database
from app.core.exceptions import FileError, DatabaseError, NotFoundError

logger = logging.getLogger(__name__)


class FilesRepository:
    """Repository for file operations using GridFS."""
    
    def __init__(self):
        """Initialize files repository."""
        self._gridfs: Optional[GridFS] = None
    
    @property
    def gridfs(self) -> GridFS:
        """Get GridFS instance.
        
        Returns:
            GridFS: GridFS instance
            
        Raises:
            DatabaseError: If GridFS access fails
        """
        if self._gridfs is None:
            self._gridfs = get_gridfs()
        return self._gridfs
    
    async def upload_file(
        self,
        file_data: Union[bytes, BinaryIO],
        filename: str,
        content_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Upload a file to GridFS.
        
        Args:
            file_data: File data (bytes or file-like object)
            filename: Original filename
            content_type: MIME content type
            metadata: Optional metadata
            
        Returns:
            str: File ID
            
        Raises:
            FileError: If upload fails
        """
        try:
            # Prepare metadata
            file_metadata = {
                "filename": filename,
                "content_type": content_type,
                "upload_date": datetime.utcnow(),
                "size": len(file_data) if isinstance(file_data, bytes) else 0,
                **(metadata or {})
            }
            
            # Upload file
            file_id = self.gridfs.put(
                file_data,
                filename=filename,
                content_type=content_type,
                metadata=file_metadata
            )
            
            logger.info(f"Uploaded file {filename} with ID: {file_id}")
            return str(file_id)
            
        except Exception as e:
            logger.error(f"Error uploading file {filename}: {e}")
            raise FileError(f"Failed to upload file: {e}")
    
    async def download_file(self, file_id: str) -> tuple[bytes, Dict[str, Any]]:
        """Download a file from GridFS.
        
        Args:
            file_id: File ID
            
        Returns:
            tuple[bytes, Dict[str, Any]]: File data and metadata
            
        Raises:
            NotFoundError: If file not found
            FileError: If download fails
        """
        try:
            object_id = ObjectId(file_id)
            grid_out = self.gridfs.get(object_id)
            
            file_data = grid_out.read()
            metadata = grid_out.metadata or {}
            
            # Add file information to metadata
            metadata.update({
                "filename": grid_out.filename,
                "content_type": grid_out.content_type,
                "upload_date": grid_out.upload_date,
                "length": grid_out.length,
                "md5": grid_out.md5
            })
            
            logger.info(f"Downloaded file with ID: {file_id}")
            return file_data, metadata
            
        except NoFile:
            logger.error(f"File not found: {file_id}")
            raise NotFoundError(f"File not found: {file_id}")
        except Exception as e:
            logger.error(f"Error downloading file {file_id}: {e}")
            raise FileError(f"Failed to download file: {e}")
    
    async def delete_file(self, file_id: str) -> bool:
        """Delete a file from GridFS.
        
        Args:
            file_id: File ID
            
        Returns:
            bool: True if deleted successfully
            
        Raises:
            FileError: If deletion fails
        """
        try:
            object_id = ObjectId(file_id)
            self.gridfs.delete(object_id)
            
            logger.info(f"Deleted file with ID: {file_id}")
            return True
            
        except NoFile:
            logger.warning(f"File not found for deletion: {file_id}")
            return False
        except Exception as e:
            logger.error(f"Error deleting file {file_id}: {e}")
            raise FileError(f"Failed to delete file: {e}")
    
    async def get_file_metadata(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get file metadata without downloading the file.
        
        Args:
            file_id: File ID
            
        Returns:
            Optional[Dict[str, Any]]: File metadata or None if not found
        """
        try:
            object_id = ObjectId(file_id)
            grid_out = self.gridfs.get(object_id)
            
            metadata = grid_out.metadata or {}
            metadata.update({
                "filename": grid_out.filename,
                "content_type": grid_out.content_type,
                "upload_date": grid_out.upload_date,
                "length": grid_out.length,
                "md5": grid_out.md5
            })
            
            return metadata
            
        except NoFile:
            logger.error(f"File not found: {file_id}")
            return None
        except Exception as e:
            logger.error(f"Error getting file metadata {file_id}: {e}")
            raise FileError(f"Failed to get file metadata: {e}")
    
    async def list_files(
        self,
        query: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        skip: int = 0
    ) -> List[Dict[str, Any]]:
        """List files in GridFS.
        
        Args:
            query: Optional query criteria
            limit: Maximum number of files to return
            skip: Number of files to skip
            
        Returns:
            List[Dict[str, Any]]: List of file metadata
        """
        try:
            files = []
            
            for grid_out in self.gridfs.find(query or {}).limit(limit).skip(skip):
                metadata = grid_out.metadata or {}
                metadata.update({
                    "_id": str(grid_out._id),
                    "filename": grid_out.filename,
                    "content_type": grid_out.content_type,
                    "upload_date": grid_out.upload_date,
                    "length": grid_out.length,
                    "md5": grid_out.md5
                })
                files.append(metadata)
            
            return files
            
        except Exception as e:
            logger.error(f"Error listing files: {e}")
            raise FileError(f"Failed to list files: {e}")
    
    async def get_file_stats(self) -> Dict[str, Any]:
        """Get GridFS statistics.
        
        Returns:
            Dict[str, Any]: GridFS statistics
        """
        try:
            db = get_database()
            
            # Get collections stats
            fs_files_stats = db.command("collstats", "fs.files")
            fs_chunks_stats = db.command("collstats", "fs.chunks")
            
            stats = {
                "total_files": fs_files_stats.get("count", 0),
                "total_chunks": fs_chunks_stats.get("count", 0),
                "total_size": fs_files_stats.get("size", 0),
                "avg_file_size": 0,
                "storage_used": fs_chunks_stats.get("size", 0)
            }
            
            # Calculate average file size
            if stats["total_files"] > 0:
                stats["avg_file_size"] = stats["total_size"] // stats["total_files"]
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting file stats: {e}")
            return {}
    
    async def cleanup_orphaned_chunks(self) -> int:
        """Clean up orphaned chunks in GridFS.
        
        Returns:
            int: Number of cleaned up chunks
        """
        try:
            db = get_database()
            
            # Find orphaned chunks (chunks without corresponding files)
            pipeline = [
                {"$lookup": {
                    "from": "fs.files",
                    "localField": "files_id",
                    "foreignField": "_id",
                    "as": "file"
                }},
                {"$match": {"file": {"$eq": []}}},
                {"$count": "orphaned_count"}
            ]
            
            result = list(db.fs.chunks.aggregate(pipeline))
            orphaned_count = result[0]["orphaned_count"] if result else 0
            
            if orphaned_count > 0:
                # Delete orphaned chunks
                db.fs.chunks.delete_many({
                    "files_id": {"$nin": [f["_id"] for f in db.fs.files.find({}, {"_id": 1})]}
                })
                
                logger.info(f"Cleaned up {orphaned_count} orphaned chunks")
            
            return orphaned_count
            
        except Exception as e:
            logger.error(f"Error cleaning up orphaned chunks: {e}")
            raise FileError(f"Failed to cleanup orphaned chunks: {e}")
    
    async def search_files(
        self,
        filename_pattern: str,
        content_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Search files by filename pattern and optionally content type.
        
        Args:
            filename_pattern: Filename pattern to search
            content_type: Optional content type filter
            limit: Maximum number of results
            
        Returns:
            List[Dict[str, Any]]: List of matching files
        """
        try:
            query = {"filename": {"$regex": filename_pattern, "$options": "i"}}
            
            if content_type:
                query["content_type"] = content_type
            
            return await self.list_files(query, limit=limit)
            
        except Exception as e:
            logger.error(f"Error searching files: {e}")
            raise FileError(f"Failed to search files: {e}")
