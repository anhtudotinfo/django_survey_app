"""
Abstract base class for storage backends.

All storage backends must implement this interface.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class StorageError(Exception):
    """Base exception for storage operations."""
    pass


class ConnectionError(StorageError):
    """Raised when connection to storage provider fails."""
    pass


class UploadError(StorageError):
    """Raised when file upload fails."""
    pass


class StorageBackend(ABC):
    """
    Abstract base class for storage backends.
    
    All storage backends must implement these methods to provide
    a consistent interface for file storage operations.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize storage backend with configuration.
        
        Args:
            config: Configuration dictionary for the backend
        """
        self.config = config or {}
    
    @abstractmethod
    def save(self, file, path: str) -> str:
        """
        Save a file to storage.
        
        Args:
            file: File object or file-like object to save
            path: Path where the file should be saved
            
        Returns:
            Storage path or identifier for the saved file
            
        Raises:
            UploadError: If file upload fails
        """
        pass
    
    @abstractmethod
    def get_url(self, path: str) -> str:
        """
        Get accessible URL for a file.
        
        Args:
            path: Storage path or identifier for the file
            
        Returns:
            Full URL where the file can be accessed
            
        Raises:
            StorageError: If URL generation fails
        """
        pass
    
    @abstractmethod
    def delete(self, path: str) -> bool:
        """
        Delete a file from storage.
        
        Args:
            path: Storage path or identifier for the file
            
        Returns:
            True if file was deleted, False if file didn't exist
            
        Raises:
            StorageError: If deletion fails
        """
        pass
    
    @abstractmethod
    def exists(self, path: str) -> bool:
        """
        Check if a file exists in storage.
        
        Args:
            path: Storage path or identifier for the file
            
        Returns:
            True if file exists, False otherwise
        """
        pass
    
    @abstractmethod
    def test_connection(self) -> Dict[str, Any]:
        """
        Test connection to storage provider.
        
        Returns:
            Dictionary with connection status and details:
            {
                'success': bool,
                'message': str,
                'details': dict (optional)
            }
        """
        pass
