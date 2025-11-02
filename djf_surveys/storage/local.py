"""
Local filesystem storage backend.

Stores files on the local filesystem using Django's FileSystemStorage.
"""

import os
from datetime import datetime
from typing import Dict, Any
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.urls import reverse
from django.utils.text import get_valid_filename
from .base import StorageBackend, UploadError, ConnectionError


class LocalStorageBackend(StorageBackend):
    """
    Local filesystem storage backend.
    
    Stores files in MEDIA_ROOT and generates absolute URLs for access.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize local storage backend.
        
        Args:
            config: Configuration dict with optional 'base_path' key
        """
        super().__init__(config)
        self.base_path = self.config.get('base_path', 'survey_uploads')
        self.storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, self.base_path))
    
    def save(self, file, path: str) -> str:
        """
        Save file to local filesystem.
        
        Args:
            file: File object to save
            path: Relative path within base directory
            
        Returns:
            Storage path relative to MEDIA_ROOT
            
        Raises:
            UploadError: If file save fails
        """
        try:
            # Clean filename to prevent path traversal
            filename = os.path.basename(path)
            clean_filename = get_valid_filename(filename)
            
            # Handle filename conflicts by adding timestamp
            if self.storage.exists(path):
                name, ext = os.path.splitext(clean_filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                clean_filename = f"{name}_{timestamp}{ext}"
                path = os.path.join(os.path.dirname(path), clean_filename)
            
            # Save the file
            saved_path = self.storage.save(path, file)
            
            # Return path relative to MEDIA_ROOT
            return os.path.join(self.base_path, saved_path)
            
        except Exception as e:
            raise UploadError(f"Failed to save file: {str(e)}")
    
    def get_url(self, path: str) -> str:
        """
        Get URL for a local file.
        
        Args:
            path: File path relative to MEDIA_ROOT
            
        Returns:
            Relative URL that Django can serve
        """
        # Remove base_path prefix if present
        if path.startswith(self.base_path):
            path = path[len(self.base_path):].lstrip('/')
        
        return self.storage.url(path)
    
    def delete(self, path: str) -> bool:
        """
        Delete a file from local storage.
        
        Args:
            path: File path relative to MEDIA_ROOT
            
        Returns:
            True if deleted, False if file didn't exist
        """
        try:
            # Remove base_path prefix if present
            if path.startswith(self.base_path):
                path = path[len(self.base_path):].lstrip('/')
            
            if self.storage.exists(path):
                self.storage.delete(path)
                return True
            return False
            
        except Exception:
            return False
    
    def exists(self, path: str) -> bool:
        """
        Check if file exists in local storage.
        
        Args:
            path: File path relative to MEDIA_ROOT
            
        Returns:
            True if file exists
        """
        # Remove base_path prefix if present
        if path.startswith(self.base_path):
            path = path[len(self.base_path):].lstrip('/')
        
        return self.storage.exists(path)
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test local storage by checking if directory is writable.
        
        Returns:
            Dictionary with connection status
        """
        try:
            # Get full directory path
            full_path = os.path.join(settings.MEDIA_ROOT, self.base_path)
            
            # Create directory if it doesn't exist
            os.makedirs(full_path, exist_ok=True)
            
            # Test if directory is writable
            test_file = os.path.join(full_path, '.write_test')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            
            return {
                'success': True,
                'message': 'Local storage is accessible and writable',
                'details': {
                    'path': full_path,
                    'writable': True
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Local storage test failed: {str(e)}',
                'details': {
                    'path': full_path if 'full_path' in locals() else None,
                    'error': str(e)
                }
            }
