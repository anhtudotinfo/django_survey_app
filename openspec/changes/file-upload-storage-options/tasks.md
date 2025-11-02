# Implementation Tasks: File Upload Storage Options

**Change ID**: `file-upload-storage-options`

## Phase 1: Storage Abstraction Layer

### 1.1 Create Storage Backend Framework
- [ ] 1.1.1 Create `djf_surveys/storage/` directory
- [ ] 1.1.2 Create `base.py` with `StorageBackend` abstract class
- [ ] 1.1.3 Define interface methods: `save()`, `get_url()`, `delete()`, `test_connection()`
- [ ] 1.1.4 Add exception classes: `StorageError`, `ConnectionError`
- [ ] 1.1.5 Add `__init__.py` with exports

### 1.2 Implement Local Storage Backend
- [ ] 1.2.1 Create `djf_surveys/storage/local.py`
- [ ] 1.2.2 Implement `LocalStorageBackend` class
- [ ] 1.2.3 Use Django's `FileSystemStorage`
- [ ] 1.2.4 Implement `save()` method with configurable path
- [ ] 1.2.5 Implement `get_url()` to generate full URL
- [ ] 1.2.6 Implement `delete()` method
- [ ] 1.2.7 Implement `test_connection()` to check directory writable
- [ ] 1.2.8 Handle file name conflicts (append timestamp)

### 1.3 Create Storage Configuration Model
- [ ] 1.3.1 Create `djf_surveys/models/storage.py`
- [ ] 1.3.2 Define `StorageConfiguration` model
- [ ] 1.3.3 Add fields: provider, credentials (JSONField), config, is_active
- [ ] 1.3.4 Add encryption for credentials field (use `django-cryptography` or similar)
- [ ] 1.3.5 Add validation for configuration
- [ ] 1.3.6 Add `get_active_storage()` class method
- [ ] 1.3.7 Add `test_connection()` method
- [ ] 1.3.8 Create migration file

### 1.4 Create Storage Manager
- [ ] 1.4.1 Create `djf_surveys/storage/manager.py`
- [ ] 1.4.2 Implement `StorageManager` class
- [ ] 1.4.3 Add `get_backend()` method to return active backend
- [ ] 1.4.4 Add caching for backend instances
- [ ] 1.4.5 Add `save_file()` convenience method
- [ ] 1.4.6 Add `get_file_url()` convenience method
- [ ] 1.4.7 Add fallback logic if configured storage fails

## Phase 2: Google Drive Integration

### 2.1 Setup Google Drive API
- [ ] 2.1.1 Add `google-auth==2.27.0` to requirements.txt
- [ ] 2.1.2 Add `google-auth-oauthlib==1.2.0` to requirements.txt
- [ ] 2.1.3 Add `google-api-python-client==2.115.0` to requirements.txt
- [ ] 2.1.4 Install dependencies in virtual environment
- [ ] 2.1.5 Create Google Cloud project (documentation)
- [ ] 2.1.6 Enable Google Drive API (documentation)
- [ ] 2.1.7 Create OAuth2 credentials (documentation)

### 2.2 Implement Google Drive Backend
- [ ] 2.2.1 Create `djf_surveys/storage/google_drive.py`
- [ ] 2.2.2 Implement `GoogleDriveBackend` class
- [ ] 2.2.3 Implement OAuth2 authentication flow
- [ ] 2.2.4 Implement token refresh logic
- [ ] 2.2.5 Implement `save()` method to upload file
- [ ] 2.2.6 Implement folder creation/organization
- [ ] 2.2.7 Implement `get_url()` to generate shareable link
- [ ] 2.2.8 Implement `delete()` method
- [ ] 2.2.9 Implement `test_connection()` method
- [ ] 2.2.10 Add retry logic for API failures
- [ ] 2.2.11 Handle rate limiting

### 2.3 OAuth2 Flow Views
- [ ] 2.3.1 Create `djf_surveys/admins/storage_views.py`
- [ ] 2.3.2 Implement `GoogleDriveAuthView` - initiate OAuth flow
- [ ] 2.3.3 Implement `GoogleDriveCallbackView` - handle callback
- [ ] 2.3.4 Store tokens in `StorageConfiguration`
- [ ] 2.3.5 Add CSRF protection
- [ ] 2.3.6 Add staff_required decorator
- [ ] 2.3.7 Add success/error messages

### 2.4 Google Drive Folder Structure
- [ ] 2.4.1 Implement folder naming: `{survey_slug}/{question_label}/`
- [ ] 2.4.2 Create folders on first upload
- [ ] 2.4.3 Cache folder IDs to avoid repeated API calls
- [ ] 2.4.4 Handle folder name sanitization
- [ ] 2.4.5 Handle duplicate file names

## Phase 3: Storage Configuration UI

### 3.1 Storage Settings Page
- [ ] 3.1.1 Create template `admins/storage_settings.html`
- [ ] 3.1.2 Create `StorageSettingsView` in `storage_views.py`
- [ ] 3.1.3 Add URL route: `/dashboard/settings/storage/`
- [ ] 3.1.4 Display current storage provider
- [ ] 3.1.5 Add radio buttons: Local / Google Drive
- [ ] 3.1.6 Add local storage path configuration field
- [ ] 3.1.7 Add "Connect Google Drive" button
- [ ] 3.1.8 Add "Test Connection" button
- [ ] 3.1.9 Add "Save Settings" button
- [ ] 3.1.10 Display connection status indicator

### 3.2 Google Drive Connection UI
- [ ] 3.2.1 Add OAuth2 flow initialization
- [ ] 3.2.2 Redirect to Google consent screen
- [ ] 3.2.3 Handle callback and token storage
- [ ] 3.2.4 Display connected account email
- [ ] 3.2.5 Add "Disconnect" button
- [ ] 3.2.6 Show token expiration status

### 3.3 Settings Form
- [ ] 3.3.1 Create `StorageConfigurationForm` in `forms.py`
- [ ] 3.3.2 Add provider choice field
- [ ] 3.3.3 Add local_path field (for local storage)
- [ ] 3.3.4 Add validation for local path
- [ ] 3.3.5 Add clean methods
- [ ] 3.3.6 Add help text

### 3.4 Navigation
- [ ] 3.4.1 Add "Storage Settings" link to admin nav
- [ ] 3.4.2 Add icon (e.g., bi-cloud-upload)
- [ ] 3.4.3 Restrict to staff users only

## Phase 4: File Upload Integration

### 4.1 Modify File Upload Views
- [ ] 4.1.1 Update `CreateSurveyFormView` to use `StorageManager`
- [ ] 4.1.2 Replace direct file.save() with storage.save_file()
- [ ] 4.1.3 Store file URL in database (not just path)
- [ ] 4.1.4 Handle storage errors gracefully
- [ ] 4.1.5 Add progress indicators for large uploads
- [ ] 4.1.6 Update success messages

### 4.2 Update Answer Model
- [ ] 4.2.1 Add `file_url` field to `Answer` model (URLField)
- [ ] 4.2.2 Keep `value` field for backward compatibility
- [ ] 4.2.3 Create migration
- [ ] 4.2.4 Add method `get_file_url()` that returns file_url or generates from value
- [ ] 4.2.5 Update save() to populate file_url

### 4.3 Update File Display
- [ ] 4.3.1 Update admin answer list to show clickable URLs
- [ ] 4.3.2 Update file download view to handle both local and Google Drive
- [ ] 4.3.3 Add file preview (if image)
- [ ] 4.3.4 Handle missing files gracefully

## Phase 5: CSV Export Enhancement

### 5.1 Modify Export Logic
- [ ] 5.1.1 Update `DownloadResponseSurveyView`
- [ ] 5.1.2 Add "File URL" column to CSV
- [ ] 5.1.3 For local files: Generate full URL using request.build_absolute_uri()
- [ ] 5.1.4 For Google Drive: Use stored shareable link
- [ ] 5.1.5 Handle multiple files (if question allows)
- [ ] 5.1.6 Add column headers in English

### 5.2 Update Export Template
- [ ] 5.2.1 Modify CSV generation to include file URLs
- [ ] 5.2.2 Format URLs as clickable (for Excel)
- [ ] 5.2.3 Add separate column for filename
- [ ] 5.2.4 Handle empty/missing files

### 5.3 Export Options
- [ ] 5.3.1 Add checkbox: "Include file URLs"
- [ ] 5.3.2 Add checkbox: "Include file content" (for images as base64 - optional)
- [ ] 5.3.3 Update export form

## Phase 6: Testing

### 6.1 Unit Tests
- [ ] 6.1.1 Test `LocalStorageBackend` methods
- [ ] 6.1.2 Test `GoogleDriveBackend` methods (with mocks)
- [ ] 6.1.3 Test `StorageManager` logic
- [ ] 6.1.4 Test `StorageConfiguration` validation
- [ ] 6.1.5 Test encryption/decryption of credentials
- [ ] 6.1.6 Test fallback logic

### 6.2 Integration Tests
- [ ] 6.2.1 Test OAuth2 flow (with test credentials)
- [ ] 6.2.2 Test file upload to local storage
- [ ] 6.2.3 Test file upload to Google Drive
- [ ] 6.2.4 Test CSV export with file URLs
- [ ] 6.2.5 Test storage switching (local → Google Drive)
- [ ] 6.2.6 Test error handling

### 6.3 End-to-End Tests
- [ ] 6.3.1 Test complete survey submission with file upload
- [ ] 6.3.2 Test admin viewing uploaded files
- [ ] 6.3.3 Test CSV export and URL access
- [ ] 6.3.4 Test storage configuration changes
- [ ] 6.3.5 Test Google Drive disconnection

## Phase 7: Documentation

### 7.1 User Documentation
- [ ] 7.1.1 Create `STORAGE_SETUP.md`
- [ ] 7.1.2 Document Google Cloud setup steps
- [ ] 7.1.3 Document OAuth2 credential creation
- [ ] 7.1.4 Document storage configuration UI
- [ ] 7.1.5 Add screenshots
- [ ] 7.1.6 Document CSV export features

### 7.2 Admin Guide
- [ ] 7.2.1 Document storage settings page
- [ ] 7.2.2 Document how to switch storage providers
- [ ] 7.2.3 Document migration considerations
- [ ] 7.2.4 Document troubleshooting steps
- [ ] 7.2.5 Document security best practices

### 7.3 Developer Documentation
- [ ] 7.3.1 Document storage backend interface
- [ ] 7.3.2 Document how to add new storage providers
- [ ] 7.3.3 Document API reference
- [ ] 7.3.4 Add code examples
- [ ] 7.3.5 Document configuration options

### 7.4 Migration Guide
- [ ] 7.4.1 Document migrating existing files to Google Drive
- [ ] 7.4.2 Provide migration script
- [ ] 7.4.3 Document rollback procedure
- [ ] 7.4.4 Document backup recommendations

## Phase 8: Security & Performance

### 8.1 Security
- [ ] 8.1.1 Encrypt stored OAuth tokens
- [ ] 8.1.2 Implement token refresh before expiration
- [ ] 8.1.3 Validate file types and sizes
- [ ] 8.1.4 Add HTTPS enforcement for file URLs
- [ ] 8.1.5 Implement rate limiting for storage operations
- [ ] 8.1.6 Add audit logging for storage configuration changes

### 8.2 Performance
- [ ] 8.2.1 Cache Google Drive folder IDs
- [ ] 8.2.2 Implement batch uploads (if needed)
- [ ] 8.2.3 Add async file upload (Celery task - optional)
- [ ] 8.2.4 Optimize CSV generation for large datasets
- [ ] 8.2.5 Add file upload progress tracking

### 8.3 Monitoring
- [ ] 8.3.1 Add logging for storage operations
- [ ] 8.3.2 Track upload success/failure rates
- [ ] 8.3.3 Monitor Google Drive API quota usage
- [ ] 8.3.4 Alert on storage failures
- [ ] 8.3.5 Track storage usage metrics

## Phase 9: Deployment

### 9.1 Environment Setup
- [ ] 9.1.1 Add environment variables for Google OAuth
- [ ] 9.1.2 Update `.env.example`
- [ ] 9.1.3 Update deployment documentation
- [ ] 9.1.4 Configure production credentials

### 9.2 Database Migration
- [ ] 9.2.1 Run migrations in staging
- [ ] 9.2.2 Test with sample data
- [ ] 9.2.3 Run migrations in production
- [ ] 9.2.4 Verify data integrity

### 9.3 Production Rollout
- [ ] 9.3.1 Deploy code to production
- [ ] 9.3.2 Configure storage settings
- [ ] 9.3.3 Test file uploads
- [ ] 9.3.4 Test CSV exports
- [ ] 9.3.5 Monitor for errors

## Task Summary

**Total Tasks**: 175  
**Estimated Effort**: 4 weeks (1 developer full-time)

**By Phase**:
- Phase 1: Storage Abstraction (22 tasks, 3 days)
- Phase 2: Google Drive Integration (26 tasks, 5 days)
- Phase 3: Configuration UI (16 tasks, 2 days)
- Phase 4: Upload Integration (12 tasks, 2 days)
- Phase 5: CSV Export (8 tasks, 1 day)
- Phase 6: Testing (15 tasks, 3 days)
- Phase 7: Documentation (15 tasks, 2 days)
- Phase 8: Security & Performance (14 tasks, 2 days)
- Phase 9: Deployment (10 tasks, 1 day)

**Priority**: High (blocks file storage scalability)  
**Complexity**: High (external API integration, OAuth)  
**Risk**: Medium (dependency on Google APIs)
