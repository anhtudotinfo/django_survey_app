# Proposal: File Upload Storage Options

**Change ID**: `file-upload-storage-options`  
**Status**: Draft  
**Created**: 2025-01-31  
**Author**: AI Assistant

## Problem Statement

Currently, file uploads in the survey system are only saved locally to the `MEDIA_ROOT` directory. This creates several limitations:

1. **No cloud backup** - Files are at risk if local storage fails
2. **No sharing capability** - Cannot easily share uploaded files via public links
3. **Limited storage management** - No control over where files are stored
4. **CSV export limitation** - Exported CSV only shows local file paths, not accessible URLs
5. **Scalability issues** - Local storage doesn't scale well for high-volume uploads

### User Pain Points

**Survey Administrators**:
- Cannot configure where uploaded files should be stored
- No automatic backup to cloud storage
- CSV exports show file paths instead of clickable links
- Difficult to share uploaded files with external parties

**System Administrators**:
- Cannot migrate storage without code changes
- No centralized control over storage providers
- Limited monitoring of storage usage

## Proposed Solution

Implement a flexible file storage system with two options:

### 1. Local Storage (Default)
- Continue supporting local file storage in `MEDIA_ROOT`
- Add configurable subdirectory structure
- Generate accessible URLs for local files

### 2. Google Drive Storage
- Integrate Google Drive API for cloud storage
- OAuth2 authentication for secure access
- Automatic folder organization by survey/question
- Generate shareable links for uploaded files

### 3. Configurable Storage Backend
- Admin UI to select storage provider (Local/Google Drive)
- Per-survey storage configuration option
- Settings page for Google Drive credentials
- Test connection before saving settings

### 4. Enhanced CSV Export
- Replace file paths with accessible URLs
- For local files: Generate full URL (http://domain/media/...)
- For Google Drive: Include shareable link
- Add column for file download link

## Success Criteria

1. ✅ Administrators can configure storage backend (Local/Google Drive)
2. ✅ Google Drive integration works with OAuth2
3. ✅ Files uploaded to surveys are stored in configured location
4. ✅ CSV exports include clickable file URLs
5. ✅ Local files generate proper URLs (not just paths)
6. ✅ Google Drive files have shareable links
7. ✅ Migration path exists for existing local files
8. ✅ Error handling for storage failures
9. ✅ Storage configuration persists in database
10. ✅ Per-survey storage override option (optional)

## Out of Scope

- Other cloud providers (AWS S3, Azure Blob, Dropbox) - future enhancement
- File encryption at rest - separate security feature
- File compression/optimization - separate feature
- File versioning - separate feature
- Bulk file migration tools - can be manual for v1

## Dependencies

### Python Packages
- `google-auth` - Google OAuth2 authentication
- `google-auth-oauthlib` - OAuth flow helpers
- `google-api-python-client` - Google Drive API client
- `django-storages` (optional) - Storage backend framework

### External Services
- Google Cloud Platform project
- Google Drive API enabled
- OAuth2 credentials (Client ID, Client Secret)

### Database Changes
- New model: `StorageConfiguration`
- Fields: provider, credentials (encrypted), is_active, created_at
- Optional: Survey.storage_config FK (for per-survey override)

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Google API quota limits | High | Implement rate limiting, batch operations |
| OAuth token expiration | Medium | Auto-refresh tokens, clear error messages |
| Network failures | Medium | Retry logic, fallback to local storage |
| Large file uploads | Medium | Stream uploads, progress indicators |
| Security of stored credentials | High | Encrypt credentials in database, use env vars |
| Migration complexity | Low | Provide clear documentation, optional migration |

## Implementation Phases

### Phase 1: Storage Abstraction Layer (Week 1)
- Create storage backend interface
- Implement LocalStorage backend
- Add storage configuration model
- Configuration UI in admin

### Phase 2: Google Drive Integration (Week 2)
- Implement GoogleDriveStorage backend
- OAuth2 flow for authentication
- Test connection functionality
- File upload/download via API

### Phase 3: CSV Export Enhancement (Week 3)
- Modify export logic to include URLs
- Generate proper URLs for local files
- Fetch shareable links from Google Drive
- Update export templates

### Phase 4: Testing & Documentation (Week 4)
- Unit tests for storage backends
- Integration tests for Google Drive
- End-to-end tests for CSV export
- User documentation
- Admin guide

## Acceptance Criteria

### Storage Configuration
- [ ] Admin can access Storage Settings page
- [ ] Can select between Local and Google Drive
- [ ] Can configure local storage path
- [ ] Can authenticate with Google OAuth2
- [ ] Can test storage connection
- [ ] Settings persist in database

### File Uploads
- [ ] Files save to configured storage
- [ ] Google Drive organizes by survey/question
- [ ] Local files save to configured path
- [ ] File metadata stored in database
- [ ] Error handling for upload failures

### CSV Export
- [ ] CSV includes "File URL" column
- [ ] Local files show full URL (e.g., http://example.com/media/...)
- [ ] Google Drive files show shareable link
- [ ] URLs are clickable/accessible
- [ ] Missing files handled gracefully

### Security
- [ ] Google credentials encrypted in database
- [ ] OAuth tokens refreshed automatically
- [ ] File access permissions respected
- [ ] HTTPS enforced for file URLs

## User Stories

### Story 1: Configure Google Drive Storage
**As a** survey administrator  
**I want to** configure Google Drive as the storage backend  
**So that** uploaded files are automatically backed up to the cloud

**Acceptance**:
- Navigate to Settings → Storage Configuration
- Click "Connect Google Drive"
- Complete OAuth2 flow
- Test connection successful
- Save settings

### Story 2: Upload File to Google Drive
**As a** survey respondent  
**I want to** upload a file in my survey response  
**So that** the file is stored securely in Google Drive

**Acceptance**:
- Fill survey with file upload question
- Select file and upload
- File saves to Google Drive in survey-specific folder
- Confirmation message shown
- File accessible later

### Story 3: Export CSV with File Links
**As a** survey administrator  
**I want to** export survey responses with file URLs  
**So that** I can easily access uploaded files

**Acceptance**:
- Navigate to survey results
- Click "Export CSV"
- CSV includes "File URL" column
- Click URL opens/downloads file
- Works for both local and Google Drive files

## Technical Notes

### Storage Backend Interface
```python
class StorageBackend:
    def save(self, file, path):
        """Save file and return URL"""
        pass
    
    def get_url(self, path):
        """Get accessible URL for file"""
        pass
    
    def delete(self, path):
        """Delete file"""
        pass
    
    def test_connection(self):
        """Test if storage is accessible"""
        pass
```

### Google Drive Folder Structure
```
Survey Uploads/
├── survey-slug-1/
│   ├── question-1-label/
│   │   ├── file-1.pdf
│   │   └── file-2.jpg
│   └── question-2-label/
│       └── file-3.docx
└── survey-slug-2/
    └── ...
```

### Configuration Model
```python
class StorageConfiguration(models.Model):
    PROVIDER_CHOICES = [
        ('local', 'Local Storage'),
        ('google_drive', 'Google Drive'),
    ]
    
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    credentials = models.JSONField(encrypted=True)  # Store OAuth tokens
    config = models.JSONField()  # Provider-specific settings
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## Open Questions

1. Should we support per-survey storage configuration? (Different surveys to different drives)
2. What should happen to existing local files when switching to Google Drive?
3. Should we implement automatic migration tool or manual process?
4. What's the file size limit for Google Drive uploads?
5. How to handle Google Drive API quota limits?
6. Should files be deleted from Google Drive when survey response is deleted?

## Related Work

- Existing: `improve-survey-ui-fileupload` - Basic file upload functionality
- Existing: `enhance-multisession-survey-ui` - Survey UI improvements
- Future: Could integrate with `AWS S3`, `Azure Blob`, `Dropbox`

## References

- [Google Drive API Documentation](https://developers.google.com/drive/api/v3/about-sdk)
- [Django File Storage](https://docs.djangoproject.com/en/stable/ref/files/storage/)
- [django-storages Documentation](https://django-storages.readthedocs.io/)
