# Technical Design: File Upload Storage Options

**Change ID**: `file-upload-storage-options`

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Django Survey App                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐         ┌──────────────┐                 │
│  │  Survey View │────────▶│Storage Manager│                 │
│  │(File Upload) │         └───────┬────────┘                 │
│  └──────────────┘                 │                          │
│                                    │                          │
│                         ┌──────────▼─────────────┐          │
│                         │  Storage Backend       │          │
│                         │     (Interface)        │          │
│                         └──────────┬─────────────┘          │
│                                    │                          │
│                   ┌────────────────┴────────────────┐       │
│                   │                                  │       │
│          ┌────────▼────────┐             ┌─────────▼──────┐ │
│          │ LocalStorage    │             │GoogleDriveStorage│
│          │   Backend       │             │    Backend       │ │
│          └────────┬────────┘             └─────────┬──────┘ │
│                   │                                  │       │
└───────────────────┼──────────────────────────────────┼───────┘
                    │                                  │
          ┌─────────▼─────────┐           ┌───────────▼────────┐
          │  Local File System│           │ Google Drive API   │
          │   (MEDIA_ROOT)    │           │   (OAuth2)         │
          └───────────────────┘           └────────────────────┘
```

## Component Details

### 1. Storage Backend Interface

**File**: `djf_surveys/storage/base.py`

```python
from abc import ABC, abstractmethod
from typing import Optional, Tuple
from django.core.files.uploadedfile import UploadedFile


class StorageBackend(ABC):
    """
    Abstract base class for file storage backends.
    
    All storage implementations must inherit from this class
    and implement the required methods.
    """
    
    @abstractmethod
    def save(self, file: UploadedFile, path: str) -> Tuple[str, str]:
        """
        Save a file to storage.
        
        Args:
            file: Django UploadedFile object
            path: Relative path where file should be saved
            
        Returns:
            Tuple of (storage_path, accessible_url)
            
        Raises:
            StorageError: If save operation fails
        """
        pass
    
    @abstractmethod
    def get_url(self, path: str) -> str:
        """
        Get accessible URL for a stored file.
        
        Args:
            path: Storage path of the file
            
        Returns:
            Fully qualified URL to access the file
            
        Raises:
            StorageError: If path doesn't exist
        """
        pass
    
    @abstractmethod
    def delete(self, path: str) -> bool:
        """
        Delete a file from storage.
        
        Args:
            path: Storage path of the file
            
        Returns:
            True if deleted successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def exists(self, path: str) -> bool:
        """
        Check if file exists in storage.
        
        Args:
            path: Storage path to check
            
        Returns:
            True if file exists, False otherwise
        """
        pass
    
    @abstractmethod
    def test_connection(self) -> Tuple[bool, str]:
        """
        Test if storage backend is accessible.
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        pass


class StorageError(Exception):
    """Base exception for storage operations"""
    pass


class ConnectionError(StorageError):
    """Raised when storage backend connection fails"""
    pass


class UploadError(StorageError):
    """Raised when file upload fails"""
    pass
```

### 2. Local Storage Backend

**File**: `djf_surveys/storage/local.py`

```python
import os
from pathlib import Path
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from .base import StorageBackend, StorageError, UploadError


class LocalStorageBackend(StorageBackend):
    """
    Local file system storage implementation.
    
    Stores files in MEDIA_ROOT with configurable subdirectory.
    """
    
    def __init__(self, base_path: str = 'uploads'):
        """
        Initialize local storage.
        
        Args:
            base_path: Subdirectory within MEDIA_ROOT (default: 'uploads')
        """
        self.base_path = base_path
        self.storage = FileSystemStorage(
            location=os.path.join(settings.MEDIA_ROOT, base_path)
        )
    
    def save(self, file, path):
        try:
            # Ensure unique filename
            filename = self.storage.get_available_name(path)
            
            # Save file
            saved_path = self.storage.save(filename, file)
            
            # Generate URL
            url = self.storage.url(saved_path)
            
            return (saved_path, url)
            
        except Exception as e:
            raise UploadError(f"Failed to save file: {str(e)}")
    
    def get_url(self, path):
        """Generate full URL for local file"""
        from django.contrib.sites.models import Site
        
        if not self.exists(path):
            raise StorageError(f"File not found: {path}")
        
        # Get relative URL
        relative_url = self.storage.url(path)
        
        # Build absolute URL
        current_site = Site.objects.get_current()
        protocol = 'https' if settings.SECURE_SSL_REDIRECT else 'http'
        absolute_url = f"{protocol}://{current_site.domain}{relative_url}"
        
        return absolute_url
    
    def delete(self, path):
        try:
            if self.exists(path):
                self.storage.delete(path)
                return True
            return False
        except Exception:
            return False
    
    def exists(self, path):
        return self.storage.exists(path)
    
    def test_connection(self):
        try:
            # Check if directory exists and is writable
            location = self.storage.location
            
            if not os.path.exists(location):
                os.makedirs(location, exist_ok=True)
            
            if not os.access(location, os.W_OK):
                return (False, f"Directory not writable: {location}")
            
            # Try to write a test file
            test_file = os.path.join(location, '.storage_test')
            try:
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
            except Exception as e:
                return (False, f"Write test failed: {str(e)}")
            
            return (True, "Local storage is accessible")
            
        except Exception as e:
            return (False, f"Connection test failed: {str(e)}")
```

### 3. Google Drive Backend

**File**: `djf_surveys/storage/google_drive.py`

```python
import io
import json
from typing import Optional
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.errors import HttpError
from .base import StorageBackend, StorageError, ConnectionError, UploadError


class GoogleDriveBackend(StorageBackend):
    """
    Google Drive storage implementation.
    
    Uses Google Drive API v3 with OAuth2 authentication.
    """
    
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    
    def __init__(self, credentials_dict: dict):
        """
        Initialize Google Drive storage.
        
        Args:
            credentials_dict: OAuth2 credentials as dictionary
        """
        self.credentials = Credentials.from_authorized_user_info(
            credentials_dict, 
            self.SCOPES
        )
        self.service = build('drive', 'v3', credentials=self.credentials)
        self.folder_cache = {}  # Cache folder IDs
    
    def _get_or_create_folder(self, folder_path: str) -> str:
        """
        Get or create folder in Google Drive.
        
        Args:
            folder_path: Path like "survey-slug/question-label"
            
        Returns:
            Folder ID
        """
        # Check cache
        if folder_path in self.folder_cache:
            return self.folder_cache[folder_path]
        
        parts = folder_path.strip('/').split('/')
        parent_id = 'root'
        
        for part in parts:
            # Search for existing folder
            query = f"name='{part}' and '{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
            
            try:
                results = self.service.files().list(
                    q=query,
                    spaces='drive',
                    fields='files(id, name)'
                ).execute()
                
                files = results.get('files', [])
                
                if files:
                    parent_id = files[0]['id']
                else:
                    # Create folder
                    file_metadata = {
                        'name': part,
                        'mimeType': 'application/vnd.google-apps.folder',
                        'parents': [parent_id]
                    }
                    
                    folder = self.service.files().create(
                        body=file_metadata,
                        fields='id'
                    ).execute()
                    
                    parent_id = folder['id']
                    
            except HttpError as e:
                raise StorageError(f"Failed to create folder: {str(e)}")
        
        # Cache the folder ID
        self.folder_cache[folder_path] = parent_id
        return parent_id
    
    def save(self, file, path):
        try:
            # Parse path: "survey-slug/question-label/filename.ext"
            parts = path.rsplit('/', 1)
            if len(parts) == 2:
                folder_path, filename = parts
            else:
                folder_path = ''
                filename = parts[0]
            
            # Get or create folder
            parent_id = 'root' if not folder_path else self._get_or_create_folder(folder_path)
            
            # Prepare file metadata
            file_metadata = {
                'name': filename,
                'parents': [parent_id]
            }
            
            # Upload file
            media = MediaIoBaseUpload(
                io.BytesIO(file.read()),
                mimetype=file.content_type or 'application/octet-stream',
                resumable=True
            )
            
            uploaded_file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink, webContentLink'
            ).execute()
            
            file_id = uploaded_file['id']
            
            # Make file accessible via link
            self.service.permissions().create(
                fileId=file_id,
                body={'type': 'anyone', 'role': 'reader'}
            ).execute()
            
            # Get shareable link
            url = uploaded_file.get('webContentLink') or uploaded_file.get('webViewLink')
            
            return (file_id, url)
            
        except HttpError as e:
            raise UploadError(f"Failed to upload to Google Drive: {str(e)}")
        except Exception as e:
            raise UploadError(f"Upload error: {str(e)}")
    
    def get_url(self, file_id: str) -> str:
        """Get shareable link for file"""
        try:
            file = self.service.files().get(
                fileId=file_id,
                fields='webContentLink, webViewLink'
            ).execute()
            
            return file.get('webContentLink') or file.get('webViewLink')
            
        except HttpError as e:
            raise StorageError(f"Failed to get file URL: {str(e)}")
    
    def delete(self, file_id: str) -> bool:
        try:
            self.service.files().delete(fileId=file_id).execute()
            return True
        except HttpError:
            return False
    
    def exists(self, file_id: str) -> bool:
        try:
            self.service.files().get(fileId=file_id).execute()
            return True
        except HttpError:
            return False
    
    def test_connection(self):
        try:
            # Try to get user info
            about = self.service.about().get(fields='user').execute()
            user_email = about['user']['emailAddress']
            
            return (True, f"Connected to Google Drive as {user_email}")
            
        except HttpError as e:
            return (False, f"Google Drive connection failed: {str(e)}")
        except Exception as e:
            return (False, f"Connection test failed: {str(e)}")
```

### 4. Storage Manager

**File**: `djf_surveys/storage/manager.py`

```python
from typing import Optional
from django.core.cache import cache
from .base import StorageBackend
from .local import LocalStorageBackend
from .google_drive import GoogleDriveBackend
from ..models import StorageConfiguration


class StorageManager:
    """
    Central manager for storage operations.
    
    Handles backend selection, caching, and fallback logic.
    """
    
    _backend_cache_key = 'active_storage_backend'
    _backend_cache_timeout = 300  # 5 minutes
    
    @classmethod
    def get_backend(cls) -> StorageBackend:
        """
        Get active storage backend.
        
        Returns cached instance if available, otherwise creates new.
        Falls back to local storage if configured storage fails.
        """
        # Try cache first
        backend = cache.get(cls._backend_cache_key)
        if backend:
            return backend
        
        # Get active configuration
        config = StorageConfiguration.get_active()
        
        if not config:
            # No configuration, use default local storage
            backend = LocalStorageBackend()
        else:
            try:
                backend = cls._create_backend(config)
            except Exception as e:
                # Log error and fallback to local
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to create storage backend: {e}")
                logger.info("Falling back to local storage")
                backend = LocalStorageBackend()
        
        # Cache backend instance
        cache.set(cls._backend_cache_key, backend, cls._backend_cache_timeout)
        
        return backend
    
    @classmethod
    def _create_backend(cls, config: StorageConfiguration) -> StorageBackend:
        """Create backend from configuration"""
        if config.provider == 'local':
            base_path = config.config.get('base_path', 'uploads')
            return LocalStorageBackend(base_path=base_path)
            
        elif config.provider == 'google_drive':
            return GoogleDriveBackend(config.credentials)
            
        else:
            raise ValueError(f"Unknown provider: {config.provider}")
    
    @classmethod
    def clear_cache(cls):
        """Clear cached backend instance"""
        cache.delete(cls._backend_cache_key)
    
    @classmethod
    def save_file(cls, file, path: str):
        """Convenience method to save file"""
        backend = cls.get_backend()
        return backend.save(file, path)
    
    @classmethod
    def get_file_url(cls, path: str) -> str:
        """Convenience method to get file URL"""
        backend = cls.get_backend()
        return backend.get_url(path)
```

### 5. Storage Configuration Model

**File**: `djf_surveys/models/storage.py`

```python
from django.db import models
from django.core.exceptions import ValidationError
from encrypted_model_fields.fields import EncryptedJSONField


class StorageConfiguration(models.Model):
    """
    Storage backend configuration.
    
    Stores provider type, credentials, and settings.
    Only one configuration can be active at a time.
    """
    
    PROVIDER_CHOICES = [
        ('local', 'Local File System'),
        ('google_drive', 'Google Drive'),
    ]
    
    provider = models.CharField(
        max_length=20,
        choices=PROVIDER_CHOICES,
        default='local'
    )
    
    credentials = EncryptedJSONField(
        default=dict,
        help_text="Encrypted OAuth tokens or API keys"
    )
    
    config = models.JSONField(
        default=dict,
        help_text="Provider-specific configuration"
    )
    
    is_active = models.BooleanField(
        default=False,
        help_text="Only one configuration can be active"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Storage Configuration"
        verbose_name_plural = "Storage Configurations"
    
    def __str__(self):
        return f"{self.get_provider_display()} ({'Active' if self.is_active else 'Inactive'})"
    
    def save(self, *args, **kwargs):
        """Ensure only one active configuration"""
        if self.is_active:
            # Deactivate all other configurations
            StorageConfiguration.objects.filter(is_active=True).update(is_active=False)
        
        super().save(*args, **kwargs)
        
        # Clear storage manager cache
        from djf_surveys.storage.manager import StorageManager
        StorageManager.clear_cache()
    
    @classmethod
    def get_active(cls):
        """Get active storage configuration"""
        return cls.objects.filter(is_active=True).first()
    
    def test_connection(self):
        """Test if this configuration works"""
        from djf_surveys.storage.manager import StorageManager
        
        backend = StorageManager._create_backend(self)
        return backend.test_connection()
    
    def clean(self):
        """Validate configuration"""
        if self.provider == 'local':
            if 'base_path' not in self.config:
                self.config['base_path'] = 'uploads'
        
        elif self.provider == 'google_drive':
            if not self.credentials:
                raise ValidationError("Google Drive requires OAuth credentials")
```

## Database Schema

```sql
-- Storage Configuration Table
CREATE TABLE djf_surveys_storageconfiguration (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider VARCHAR(20) NOT NULL DEFAULT 'local',
    credentials TEXT NOT NULL,  -- Encrypted JSON
    config TEXT NOT NULL,       -- JSON
    is_active BOOLEAN NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

-- Index for active configuration lookup
CREATE INDEX idx_storage_active ON djf_surveys_storageconfiguration(is_active);

-- Update Answer model to include file_url
ALTER TABLE djf_surveys_answer ADD COLUMN file_url VARCHAR(500);
```

## API Flow Diagrams

### File Upload Flow

```
User                Survey View         Storage Manager      Backend           Google Drive
 |                      |                      |                |                    |
 |--Submit form-------->|                      |                |                    |
 |  with file          |                      |                |                    |
 |                      |                      |                |                    |
 |                      |--save_file()-------->|                |                    |
 |                      |                      |                |                    |
 |                      |                      |--get_backend()->|                    |
 |                      |                      |                |                    |
 |                      |                      |--save()-------->|                    |
 |                      |                      |                |                    |
 |                      |                      |                |--create_folder()-->|
 |                      |                      |                |<--folder_id--------|
 |                      |                      |                |                    |
 |                      |                      |                |--upload_file()---->|
 |                      |                      |                |<--file_id----------|
 |                      |                      |                |                    |
 |                      |                      |                |--set_permissions-->|
 |                      |                      |                |<--success----------|
 |                      |                      |                |                    |
 |                      |                      |<--(path, url)--|                    |
 |                      |<--(path, url)--------|                |                    |
 |                      |                      |                |                    |
 |                      |--Save to DB--------->|                |                    |
 |                      |  (file_url)          |                |                    |
 |                      |                      |                |                    |
 |<--Success response---|                      |                |                    |
```

### CSV Export Flow

```
Admin               Export View         Answer Model        Storage Backend
 |                      |                      |                    |
 |--Click export------->|                      |                    |
 |                      |                      |                    |
 |                      |--get_answers()------>|                    |
 |                      |<--answer_list--------|                    |
 |                      |                      |                    |
 |                      | For each answer:     |                    |
 |                      |--get_file_url()----->|                    |
 |                      |                      |--get_url()-------->|
 |                      |                      |<--full_url---------|
 |                      |<--file_url-----------|                    |
 |                      |                      |                    |
 |                      |--Generate CSV------->|                    |
 |                      |  with URLs           |                    |
 |                      |                      |                    |
 |<--Download CSV-------|                      |                    |
```

## Security Considerations

### 1. Credential Storage
- OAuth tokens stored encrypted in database
- Use `django-encrypted-model-fields` or `django-cryptography`
- Never log credentials
- Rotate encryption keys periodically

### 2. File Access Control
- Google Drive files: Set to "anyone with link can view"
- Local files: Serve through Django view with permission checks
- Validate file types on upload
- Implement file size limits

### 3. OAuth Flow
- Use CSRF protection on callback
- Validate state parameter
- Store tokens securely
- Implement token refresh before expiration

### 4. API Security
- Rate limit storage operations
- Implement retry with exponential backoff
- Handle quota exceeded errors gracefully
- Log all storage operations for audit

## Performance Optimization

### 1. Caching Strategy
```python
# Cache folder IDs to avoid repeated API calls
folder_cache = {
    "survey-slug-1/question-label-1": "1a2b3c4d5e",
    "survey-slug-1/question-label-2": "2b3c4d5e6f",
}

# Cache backend instance for 5 minutes
cache.set('storage_backend', backend, timeout=300)
```

### 2. Batch Operations
```python
# Upload multiple files in parallel
import concurrent.futures

def upload_files_batch(files, paths):
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(storage.save, file, path)
            for file, path in zip(files, paths)
        ]
        return [f.result() for f in futures]
```

### 3. Async Upload (Optional)
```python
# Use Celery for large file uploads
@shared_task
def upload_file_async(file_data, path):
    storage = StorageManager.get_backend()
    return storage.save(file_data, path)
```

## Configuration Examples

### Local Storage Config
```json
{
  "provider": "local",
  "config": {
    "base_path": "uploads",
    "max_file_size": 10485760,  // 10MB
    "allowed_extensions": [".pdf", ".jpg", ".png", ".docx"]
  },
  "credentials": {},
  "is_active": true
}
```

### Google Drive Config
```json
{
  "provider": "google_drive",
  "config": {
    "root_folder": "Survey Uploads",
    "max_file_size": 52428800,  // 50MB
    "share_publicly": true
  },
  "credentials": {
    "token": "ya29.a0AfH6...",
    "refresh_token": "1//0gZxxx...",
    "token_uri": "https://oauth2.googleapis.com/token",
    "client_id": "123456789.apps.googleusercontent.com",
    "client_secret": "GOCSPX-xxx...",
    "scopes": ["https://www.googleapis.com/auth/drive.file"]
  },
  "is_active": true
}
```

## Error Handling

### Error Types and Recovery
```python
try:
    storage.save(file, path)
except ConnectionError:
    # Network/API unavailable
    # Retry with exponential backoff
    # Or fallback to local storage
except UploadError:
    # File upload failed
    # Check file size, type
    # Show user-friendly error
except StorageError:
    # Generic storage error
    # Log details
    # Notify admin
```

## Testing Strategy

### Unit Tests
- Mock Google Drive API responses
- Test each backend independently
- Test encryption/decryption of credentials
- Test fallback logic

### Integration Tests
- Use test Google account
- Test OAuth flow end-to-end
- Test file upload → CSV export flow
- Test storage switching

### Performance Tests
- Upload 100+ files
- Measure API call latency
- Test concurrent uploads
- Monitor memory usage

## Deployment Checklist

- [ ] Add environment variables for Google OAuth
- [ ] Run database migrations
- [ ] Configure storage settings
- [ ] Test file upload
- [ ] Test CSV export
- [ ] Set up monitoring/alerts
- [ ] Document setup for ops team
- [ ] Train administrators

## Future Enhancements

1. **Additional Providers**: AWS S3, Azure Blob, Dropbox
2. **File Compression**: Automatic compression before upload
3. **Image Optimization**: Resize/compress images
4. **File Versioning**: Keep file history
5. **Bulk Migration Tool**: Migrate all local files to cloud
6. **Storage Analytics**: Dashboard for storage usage
7. **CDN Integration**: Serve files through CDN
8. **File Encryption**: End-to-end encryption
9. **Webhook Notifications**: Alert on upload/delete
10. **Multi-region Support**: Store files in different regions
