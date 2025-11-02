# Spec Delta: Survey Field Types

**Capability**: `survey-field-types`  
**Change**: `enhance-file-storage-and-branching-ui`

## ADDED Requirements

### Requirement: File Storage Backend Configuration

The system SHALL support multiple storage backends for file upload questions.

#### Scenario: Configure local file storage
- **WHEN** administrator accesses storage settings
- **THEN** option to select "Local File System" is available
- **WHEN** local storage is selected and configured
- **THEN** uploaded files are saved to configurable subdirectory in MEDIA_ROOT
- **AND** files generate absolute URLs for access

#### Scenario: Configure Google Drive storage
- **WHEN** administrator accesses storage settings
- **THEN** option to select "Google Drive" is available
- **WHEN** administrator clicks "Connect Google Drive"
- **THEN** OAuth2 authentication flow is initiated
- **WHEN** OAuth flow completes successfully
- **THEN** Google Drive credentials are stored encrypted
- **AND** uploaded files are saved to Google Drive
- **AND** files are organized in folder structure: Survey Uploads/{survey_slug}/{question_label}/

#### Scenario: Test storage connection
- **WHEN** administrator configures storage backend
- **AND** clicks "Test Connection" button
- **THEN** system verifies storage is accessible
- **AND** displays success message if connection works
- **OR** displays error message with details if connection fails
- **AND** settings cannot be saved until connection test passes

### Requirement: File URL Generation

The system SHALL generate accessible URLs for uploaded files regardless of storage backend.

#### Scenario: Generate URL for local file
- **WHEN** file is uploaded to local storage
- **THEN** system generates absolute URL using site domain
- **AND** URL format is: `https://{domain}/media/survey_uploads/{survey_id}/{answer_id}/{filename}`
- **AND** URL is stored in Answer.file_url field

#### Scenario: Generate URL for Google Drive file
- **WHEN** file is uploaded to Google Drive
- **THEN** system creates shareable link with "anyone with link can view" permission
- **AND** URL is stored in Answer.file_url field
- **AND** URL allows direct download without authentication

#### Scenario: Retrieve file URL for display
- **WHEN** administrator views survey responses
- **AND** response includes file upload
- **THEN** file is displayed as clickable link with filename
- **WHEN** file URL exists in Answer.file_url
- **THEN** that URL is used
- **OR** URL is generated from Answer.value (backward compatibility)

## MODIFIED Requirements

### Requirement: File Upload Storage

The system SHALL store uploaded files in configured storage backend (local or Google Drive).

#### Scenario: Upload file with configured storage
- **WHEN** user uploads file in survey response
- **THEN** file is saved to active storage backend
- **AND** storage path or identifier is stored in Answer.value
- **AND** accessible URL is stored in Answer.file_url
- **AND** user receives confirmation of successful upload

#### Scenario: Switch storage providers
- **WHEN** administrator changes active storage backend
- **THEN** new uploads use new storage backend
- **AND** existing files remain accessible via stored URLs
- **AND** no data migration is required (existing files continue to work)

#### Scenario: Storage failure fallback
- **WHEN** file upload fails due to storage error
- **AND** configured storage is not local
- **THEN** system attempts to fall back to local storage
- **AND** logs error for administrator review
- **OR** displays user-friendly error message if fallback also fails

## REMOVED Requirements

None
