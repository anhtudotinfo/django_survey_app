"""
Google Drive storage backend.

Stores files in Google Drive using the Drive API v3.
Requires OAuth2 authentication.
"""

import io
import logging
from typing import Dict, Any, Optional
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.errors import HttpError
from google.auth.exceptions import RefreshError
from .base import StorageBackend, UploadError, ConnectionError, StorageError

logger = logging.getLogger(__name__)

# Google Drive API scopes
SCOPES = ['https://www.googleapis.com/auth/drive.file']


class GoogleDriveBackend(StorageBackend):
    """
    Google Drive storage backend.
    
    Uploads files to Google Drive and provides shareable links.
    Organizes files in folders matching the survey structure.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize Google Drive backend.
        
        Args:
            config: Configuration dict with 'credentials' key containing OAuth2 tokens
        """
        super().__init__(config)
        self.service = None
        self.folder_cache = {}  # Cache folder IDs
        
        # Initialize service
        try:
            self._init_service()
        except Exception as e:
            logger.error(f"Failed to initialize Google Drive service: {e}")
            raise ConnectionError(f"Failed to connect to Google Drive: {str(e)}")
    
    def _init_service(self):
        """Initialize Google Drive API service."""
        credentials_data = self.config.get('credentials', {})
        
        if not credentials_data:
            raise ConnectionError("No credentials provided for Google Drive")
        
        try:
            # Create credentials from stored tokens
            credentials = Credentials(
                token=credentials_data.get('token'),
                refresh_token=credentials_data.get('refresh_token'),
                token_uri=credentials_data.get('token_uri', 'https://oauth2.googleapis.com/token'),
                client_id=credentials_data.get('client_id'),
                client_secret=credentials_data.get('client_secret'),
                scopes=SCOPES
            )
            
            # Build service
            self.service = build('drive', 'v3', credentials=credentials, cache_discovery=False)
            
        except Exception as e:
            logger.error(f"Failed to create Drive service: {e}")
            raise ConnectionError(f"Failed to authenticate with Google Drive: {str(e)}")
    
    def _get_or_create_folder(self, folder_path: str, parent_id: str = None) -> str:
        """
        Get or create a folder in Google Drive.
        
        Args:
            folder_path: Folder path (e.g., "survey_uploads/survey_1")
            parent_id: Parent folder ID (None = root)
            
        Returns:
            Folder ID
        """
        # Check cache
        cache_key = f"{parent_id}:{folder_path}"
        if cache_key in self.folder_cache:
            return self.folder_cache[cache_key]
        
        # Split path into parts
        parts = folder_path.strip('/').split('/')
        current_parent = parent_id
        
        for folder_name in parts:
            # Search for folder
            query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
            if current_parent:
                query += f" and '{current_parent}' in parents"
            query += " and trashed=false"
            
            try:
                results = self.service.files().list(
                    q=query,
                    spaces='drive',
                    fields='files(id, name)',
                    pageSize=1
                ).execute()
                
                files = results.get('files', [])
                
                if files:
                    # Folder exists
                    current_parent = files[0]['id']
                else:
                    # Create folder
                    file_metadata = {
                        'name': folder_name,
                        'mimeType': 'application/vnd.google-apps.folder'
                    }
                    if current_parent:
                        file_metadata['parents'] = [current_parent]
                    
                    folder = self.service.files().create(
                        body=file_metadata,
                        fields='id'
                    ).execute()
                    
                    current_parent = folder['id']
                    logger.info(f"Created folder: {folder_name} (ID: {current_parent})")
                
            except HttpError as e:
                logger.error(f"Google Drive API error: {e}")
                raise StorageError(f"Failed to create/find folder: {str(e)}")
        
        # Cache the folder ID
        self.folder_cache[cache_key] = current_parent
        return current_parent
    
    def save(self, file, path: str) -> str:
        """
        Upload file to Google Drive.
        
        Args:
            file: File object to upload
            path: Destination path (e.g., "survey_1/question_5/file.pdf")
            
        Returns:
            Google Drive file ID
        """
        try:
            # Parse path
            parts = path.rsplit('/', 1)
            if len(parts) == 2:
                folder_path, filename = parts
            else:
                folder_path = None
                filename = parts[0]
            
            # Get or create folder
            parent_id = None
            if folder_path:
                parent_id = self._get_or_create_folder(folder_path)
            
            # Prepare file metadata
            file_metadata = {'name': filename}
            if parent_id:
                file_metadata['parents'] = [parent_id]
            
            # Read file content
            file.seek(0)
            file_content = file.read()
            file.seek(0)
            
            # Upload file
            media = MediaIoBaseUpload(
                io.BytesIO(file_content),
                mimetype='application/octet-stream',
                resumable=True
            )
            
            drive_file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink'
            ).execute()
            
            file_id = drive_file['id']
            logger.info(f"Uploaded file to Google Drive: {filename} (ID: {file_id})")
            
            # Make file accessible with link
            self.service.permissions().create(
                fileId=file_id,
                body={'type': 'anyone', 'role': 'reader'}
            ).execute()
            
            return file_id
            
        except HttpError as e:
            logger.error(f"Google Drive upload failed: {e}")
            raise UploadError(f"Failed to upload to Google Drive: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during upload: {e}")
            raise UploadError(f"Upload failed: {str(e)}")
    
    def get_url(self, path: str) -> str:
        """
        Get shareable URL for a Google Drive file.
        
        Args:
            path: Google Drive file ID
            
        Returns:
            Direct download URL
        """
        try:
            # Get file metadata
            file = self.service.files().get(
                fileId=path,
                fields='webContentLink, webViewLink'
            ).execute()
            
            # Return download link (prefer webContentLink, fallback to webViewLink)
            return file.get('webContentLink') or file.get('webViewLink', '')
            
        except HttpError as e:
            logger.error(f"Failed to get file URL: {e}")
            # Return a generic Drive URL
            return f"https://drive.google.com/file/d/{path}/view"
    
    def delete(self, path: str) -> bool:
        """
        Delete file from Google Drive.
        
        Args:
            path: Google Drive file ID
            
        Returns:
            True if deleted, False if not found
        """
        try:
            self.service.files().delete(fileId=path).execute()
            logger.info(f"Deleted file from Google Drive: {path}")
            return True
            
        except HttpError as e:
            if e.resp.status == 404:
                return False
            logger.error(f"Failed to delete file: {e}")
            return False
    
    def exists(self, path: str) -> bool:
        """
        Check if file exists in Google Drive.
        
        Args:
            path: Google Drive file ID
            
        Returns:
            True if file exists
        """
        try:
            self.service.files().get(fileId=path, fields='id').execute()
            return True
        except HttpError as e:
            if e.resp.status == 404:
                return False
            logger.error(f"Error checking file existence: {e}")
            return False
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test Google Drive connection by listing files.
        
        Returns:
            Dictionary with connection status
        """
        try:
            # Try to list files (limited to 1)
            results = self.service.files().list(pageSize=1, fields='files(id, name)').execute()
            
            # Get user info
            about = self.service.about().get(fields='user').execute()
            user_email = about.get('user', {}).get('emailAddress', 'Unknown')
            
            return {
                'success': True,
                'message': 'Successfully connected to Google Drive',
                'details': {
                    'connected_as': user_email,
                    'provider': 'Google Drive'
                }
            }
            
        except RefreshError:
            return {
                'success': False,
                'message': 'Google Drive token expired. Please re-authenticate.',
                'details': {'error': 'token_expired'}
            }
        except HttpError as e:
            return {
                'success': False,
                'message': f'Google Drive API error: {str(e)}',
                'details': {'error': str(e)}
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Connection test failed: {str(e)}',
                'details': {'error': str(e)}
            }
