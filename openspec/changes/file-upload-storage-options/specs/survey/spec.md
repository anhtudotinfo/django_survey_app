# Survey: File Upload Storage Options (Delta)

**Change ID**: `file-upload-storage-options`  
**Capability**: Survey

## ADDED Requirements

### Requirement: Storage Backend Configuration

Survey system SHALL support configurable file storage backends including local file system and Google Drive cloud storage.

**Context**: Allow administrators to choose where uploaded survey files are stored, enabling cloud backup and scalability.

#### Scenario: Administrator configures local storage
**Given** an administrator is logged into the admin panel  
**And** navigates to "Storage Settings"  
**When** they select "Local File System" as the storage provider  
**And** configure the base path as "uploads/surveys"  
**And** click "Test Connection"  
**Then** the system verifies the directory exists and is writable  
**And** displays "Connection successful" message  
**When** they click "Save Settings"  
**Then** the configuration is stored in the database  
**And** all new file uploads use local storage

#### Scenario: Administrator connects Google Drive
**Given** an administrator is logged into the admin panel  
**And** navigates to "Storage Settings"  
**When** they select "Google Drive" as the storage provider  
**And** click "Connect Google Drive"  
**Then** they are redirected to Google OAuth2 consent screen  
**When** they approve access to Google Drive  
**Then** they are redirected back to settings page  
**And** see "Connected as user@gmail.com"  
**When** they click "Test Connection"  
**Then** the system verifies Google Drive API access  
**And** displays "Connected to Google Drive" message  
**When** they click "Save Settings"  
**Then** OAuth tokens are encrypted and stored in database  
**And** all new file uploads use Google Drive

### Requirement: File Upload with Configurable Storage

When users upload files in survey responses, files SHALL be saved to the configured storage backend and accessible URLs SHALL be stored.

**Context**: Transparently use configured storage (local or Google Drive) without changing user experience.

#### Scenario: User uploads file to local storage
**Given** local storage is configured as active backend  
**And** a user is filling out a survey with file upload question  
**When** they select a file "document.pdf" and submit  
**Then** the file is saved to local file system in "uploads/surveys/{survey-slug}/{question-label}/"  
**And** a full accessible URL is generated like "https://example.com/media/uploads/surveys/feedback/resume/document.pdf"  
**And** the URL is stored in Answer.file_url field  
**And** the user sees "File uploaded successfully"

#### Scenario: User uploads file to Google Drive
**Given** Google Drive is configured as active backend  
**And** a user is filling out a survey with file upload question  
**When** they select a file "photo.jpg" and submit  
**Then** the file is uploaded to Google Drive in folder "Survey Uploads/{survey-slug}/{question-label}/"  
**And** file is set to "anyone with link can view"  
**And** a shareable link is generated like "https://drive.google.com/file/d/FILE_ID/view"  
**And** the link is stored in Answer.file_url field  
**And** the user sees "File uploaded successfully"

#### Scenario: File upload fails with network error
**Given** Google Drive is configured as active backend  
**And** network connection to Google API fails  
**When** a user tries to upload a file  
**Then** the system retries upload 3 times with exponential backoff  
**When** all retries fail  
**Then** the system falls back to local storage  
**And** logs the error for administrator review  
**And** the user sees "File uploaded (using backup storage)"

### Requirement: CSV Export with File URLs

Survey response exports SHALL include accessible URLs for uploaded files instead of just file paths.

**Context**: Make it easy for administrators to access uploaded files directly from CSV exports.

#### Scenario: Export CSV with local file URLs
**Given** a survey has 10 responses with file uploads  
**And** files are stored in local storage  
**When** an administrator clicks "Export CSV"  
**Then** the CSV includes a "File URL" column  
**And** each row shows full URL like "https://example.com/media/uploads/surveys/feedback/resume/file1.pdf"  
**And** URLs are clickable in Excel/Google Sheets  
**When** administrator clicks a URL  
**Then** the file downloads or opens in browser

#### Scenario: Export CSV with Google Drive links
**Given** a survey has 10 responses with file uploads  
**And** files are stored in Google Drive  
**When** an administrator clicks "Export CSV"  
**Then** the CSV includes a "File URL" column  
**And** each row shows Google Drive link like "https://drive.google.com/file/d/FILE_ID/view"  
**And** URLs are clickable in Excel/Google Sheets  
**When** administrator clicks a URL  
**Then** Google Drive opens the file for viewing or downloading

#### Scenario: Export CSV with mixed storage
**Given** a survey initially used local storage  
**And** administrator switched to Google Drive  
**And** now has 5 responses with local files and 5 with Google Drive files  
**When** administrator exports CSV  
**Then** the CSV includes "File URL" column  
**And** local file rows show "https://example.com/media/..." URLs  
**And** Google Drive file rows show "https://drive.google.com/file/..." URLs  
**And** all URLs are accessible

#### Scenario: Handle missing files in export
**Given** a survey response had a file upload  
**And** the file was manually deleted from storage  
**When** administrator exports CSV  
**Then** the CSV includes "File URL" column  
**And** the row for missing file shows "(File not found)"  
**And** export completes without errors

## MODIFIED Requirements

### Requirement: File Upload Question Type

Survey questions with type "File Upload" SHALL support uploading files through the configured storage backend with validation.

**Changes**:
- Uses StorageManager instead of direct file.save()
- Stores file_url in addition to file path
- Supports both local and cloud storage transparently

#### Scenario: File upload saves to configured storage
**Given** a survey has a file upload question  
**And** storage backend is configured (local or Google Drive)  
**When** user uploads a file  
**Then** StorageManager.save_file() is called with file and path  
**And** file is saved to configured backend  
**And** both storage_path and accessible_url are returned  
**And** both are stored in Answer model (value = path, file_url = url)

## Technical Implementation Notes

### New Models

**StorageConfiguration**:
- `provider`: CharField (choices: 'local', 'google_drive')
- `credentials`: EncryptedJSONField (OAuth tokens)
- `config`: JSONField (provider-specific settings)
- `is_active`: BooleanField (only one active at a time)
- `created_at`, `updated_at`: DateTimeField

**Answer Model Changes**:
- Add `file_url`: URLField(max_length=500, null=True, blank=True)
- Keep `value` for backward compatibility (stores path or file_id)

### New Components

**Storage Backends**:
- `djf_surveys/storage/base.py`: Abstract base class
- `djf_surveys/storage/local.py`: Local file system implementation
- `djf_surveys/storage/google_drive.py`: Google Drive API implementation
- `djf_surveys/storage/manager.py`: Central manager with caching

**Admin Views**:
- Storage Settings page (`/dashboard/settings/storage/`)
- Google OAuth callback handler
- Test connection endpoint

### API Integration

**Google Drive API**:
- OAuth2 flow for authentication
- Files API v3 for file operations
- Permissions API for sharing settings

### Security

- OAuth tokens encrypted using `django-encrypted-model-fields`
- CSRF protection on OAuth callback
- File size and type validation
- HTTPS enforcement for file URLs

### Performance

- Cache storage backend instances (5 min TTL)
- Cache Google Drive folder IDs
- Retry logic with exponential backoff
- Fallback to local storage on cloud errors
