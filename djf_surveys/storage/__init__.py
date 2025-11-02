"""
Storage backend framework for survey file uploads.

Supports multiple storage backends (local filesystem, Google Drive, etc.)
with a unified interface.
"""

from .manager import StorageManager
from .base import StorageBackend, StorageError, ConnectionError, UploadError
from .local import LocalStorageBackend

__all__ = [
    'StorageManager', 
    'StorageBackend', 
    'StorageError', 
    'ConnectionError', 
    'UploadError',
    'LocalStorageBackend'
]
