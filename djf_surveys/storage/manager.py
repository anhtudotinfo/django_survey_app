"""
Storage manager for handling file storage operations.

Provides a unified interface for saving, retrieving, and deleting files
across different storage backends.
"""

import logging
from typing import Optional, Dict, Any
from django.core.cache import cache
from .base import StorageBackend, StorageError
from .local import LocalStorageBackend

logger = logging.getLogger(__name__)

STORAGE_CACHE_KEY = 'djf_surveys_storage_backend'
STORAGE_CACHE_TIMEOUT = 300  # 5 minutes


class StorageManager:
    """
    Manages file storage operations across different backends.
    
    Features:
    - Factory pattern for creating backend instances
    - Caching of backend instances (5 min TTL)
    - Automatic fallback to local storage on errors
    - Convenience methods for common operations
    """
    
    def __init__(self):
        """Initialize storage manager."""
        self._backend_cache = {}
    
    def get_backend(self) -> StorageBackend:
        """
        Get the active storage backend instance.
        
        Checks cache first, then creates new instance if needed.
        Falls back to local storage if configured backend fails.
        
        Returns:
            StorageBackend instance
        """
        # Check memory cache first
        cached_backend = cache.get(STORAGE_CACHE_KEY)
        if cached_backend:
            return cached_backend
        
        # Get active configuration from database
        from djf_surveys.models import StorageConfiguration
        
        try:
            config = StorageConfiguration.get_active()
            
            if config:
                backend = self._create_backend(
                    config.provider,
                    config.config,
                    config.credentials
                )
            else:
                # No configuration - use local storage by default
                logger.info("No active storage configuration, using local storage")
                backend = LocalStorageBackend()
            
            # Cache the backend
            cache.set(STORAGE_CACHE_KEY, backend, STORAGE_CACHE_TIMEOUT)
            return backend
            
        except Exception as e:
            logger.error(f"Failed to get storage backend: {e}, falling back to local storage")
            backend = LocalStorageBackend()
            cache.set(STORAGE_CACHE_KEY, backend, STORAGE_CACHE_TIMEOUT)
            return backend
    
    def _create_backend(self, provider: str, config: Dict[str, Any], credentials: Dict[str, Any]) -> StorageBackend:
        """
        Factory method to create storage backend instances.
        
        Args:
            provider: Backend provider name ('local' or 'google_drive')
            config: Configuration dictionary
            credentials: Credentials dictionary
            
        Returns:
            StorageBackend instance
            
        Raises:
            StorageError: If provider is unknown
        """
        if provider == 'local':
            return LocalStorageBackend(config)
        
        elif provider == 'google_drive':
            from .google_drive import GoogleDriveBackend
            # Merge credentials into config for GoogleDriveBackend
            full_config = {**config, 'credentials': credentials}
            return GoogleDriveBackend(full_config)
        
        else:
            raise StorageError(f"Unknown storage provider: {provider}")
    
    def clear_cache(self):
        """Clear the backend cache."""
        cache.delete(STORAGE_CACHE_KEY)
        logger.info("Storage backend cache cleared")
    
    # Convenience methods
    
    def save_file(self, file, path: str) -> str:
        """
        Save a file using the active backend.
        
        Args:
            file: File object to save
            path: Destination path
            
        Returns:
            Storage path or identifier
        """
        backend = self.get_backend()
        return backend.save(file, path)
    
    def get_file_url(self, path: str) -> str:
        """
        Get URL for a file.
        
        Args:
            path: Storage path or identifier
            
        Returns:
            Accessible URL
        """
        backend = self.get_backend()
        return backend.get_url(path)
    
    def delete_file(self, path: str) -> bool:
        """
        Delete a file.
        
        Args:
            path: Storage path or identifier
            
        Returns:
            True if deleted, False if not found
        """
        backend = self.get_backend()
        return backend.delete(path)
    
    def file_exists(self, path: str) -> bool:
        """
        Check if a file exists.
        
        Args:
            path: Storage path or identifier
            
        Returns:
            True if exists
        """
        backend = self.get_backend()
        return backend.exists(path)
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test connection to active backend.
        
        Returns:
            Dictionary with status and details
        """
        backend = self.get_backend()
        return backend.test_connection()
