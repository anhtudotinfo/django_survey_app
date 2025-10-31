# Survey Field Types Capability

## ADDED Requirements

### Requirement: File Upload Field Type
The system SHALL support file upload as a question type, allowing users to attach files in their responses.

#### Scenario: Create file upload question
- **WHEN** admin creates question with type "File Upload"
- **THEN** question is saved with type_field = TYPE_FIELD.file (value 10)
- **AND** field accepts file input during survey completion
- **AND** help text can specify allowed file types

#### Scenario: Upload file in survey response
- **WHEN** user selects file in file upload question
- **AND** file meets validation criteria (type, size)
- **AND** submits section or survey
- **THEN** file is uploaded to server
- **AND** file path is stored in Answer.file_value field
- **AND** original filename is preserved in storage path

#### Scenario: Display uploaded file in response
- **WHEN** admin views user response with file upload
- **THEN** filename is displayed as clickable link
- **AND** clicking link downloads or displays file
- **AND** file is served through protected view (permission check)

### Requirement: File Type Validation
The system SHALL validate uploaded files to ensure only allowed types are accepted.

#### Scenario: Accept allowed file types
- **WHEN** user uploads file with extension in allowed list
- **THEN** file is accepted and uploaded
- **AND** allowed types include: jpg, jpeg, png, gif (images), pdf, doc, docx, xls, xlsx (documents)

#### Scenario: Reject disallowed file types
- **WHEN** user uploads file with disallowed extension (e.g., .exe, .sh, .bat)
- **THEN** upload is rejected immediately
- **AND** user sees error: "File type not allowed. Allowed types: jpg, png, pdf, docx..."
- **AND** form does not submit until valid file selected or field cleared

#### Scenario: Validate MIME type
- **WHEN** file is uploaded
- **THEN** system checks both file extension and MIME type
- **AND** rejects if MIME type doesn't match extension
- **AND** prevents malicious files with fake extensions

### Requirement: File Size Limits
The system SHALL enforce file size limits to prevent storage abuse and upload issues.

#### Scenario: Accept files under limit
- **WHEN** user uploads file with size ≤ 10MB
- **THEN** file is accepted and uploaded successfully

#### Scenario: Reject oversized files
- **WHEN** user uploads file > 10MB
- **THEN** upload is rejected
- **AND** user sees error: "File too large. Maximum size: 10MB"
- **AND** form validation fails

#### Scenario: Configurable size limit
- **WHEN** admin sets SURVEY_FILE_UPLOAD_MAX_SIZE setting
- **THEN** system uses configured value instead of default 10MB
- **AND** error messages reflect actual limit

### Requirement: File Storage Security
The system SHALL store uploaded files securely with access control.

#### Scenario: Store files in private location
- **WHEN** file is uploaded
- **THEN** file is stored outside public web root
- **AND** path structure: survey_uploads/{survey_id}/{user_answer_id}/{filename}
- **AND** files cannot be directly accessed via URL

#### Scenario: Controlled file access
- **WHEN** user or admin requests uploaded file
- **THEN** request goes through Django view with permission check
- **AND** authenticated admin users can access any survey file
- **AND** survey respondent can access only their own files
- **AND** private_response setting is respected
- **AND** unauthorized access returns 403 error

#### Scenario: Prevent path traversal
- **WHEN** file is uploaded with malicious filename (e.g., ../../etc/passwd)
- **THEN** system sanitizes filename
- **AND** removes path separators and special characters
- **AND** generates safe filename preserving extension

### Requirement: File Upload UI
The system SHALL provide intuitive file upload interface in survey forms.

#### Scenario: Display file input
- **WHEN** user views file upload question
- **THEN** standard file input button is displayed
- **AND** help text shows allowed types and size limit
- **AND** required indicator shows if field is mandatory

#### Scenario: Show selected filename
- **WHEN** user selects file
- **THEN** filename is displayed next to input
- **AND** file size is shown
- **AND** "Change" or "Remove" option is available

#### Scenario: Client-side validation feedback
- **WHEN** user selects invalid file (wrong type or too large)
- **THEN** immediate feedback is shown (before form submit)
- **AND** user can select different file
- **AND** server-side validation still occurs

### Requirement: File Upload in Drafts
The system SHALL handle file uploads correctly in draft responses.

#### Scenario: Save draft with uploaded file
- **WHEN** user uploads file and saves draft
- **THEN** file is stored immediately
- **AND** draft references file path
- **AND** resuming draft shows filename as uploaded

#### Scenario: Replace file in draft
- **WHEN** user resumes draft with uploaded file
- **AND** uploads different file to same question
- **THEN** old file is marked for deletion
- **AND** new file replaces it in draft
- **AND** old file is cleaned up if draft expires or survey submitted

#### Scenario: Delete file in draft
- **WHEN** user resumes draft and removes uploaded file
- **THEN** file is marked for deletion
- **AND** draft no longer references file
- **AND** file is cleaned up appropriately

### Requirement: File Cleanup
The system SHALL provide mechanisms to clean up orphaned and old files.

#### Scenario: Delete files with survey deletion
- **WHEN** admin deletes survey
- **THEN** all associated uploaded files are deleted from storage
- **AND** database records are cleaned via CASCADE delete

#### Scenario: Cleanup orphaned files
- **WHEN** scheduled cleanup job runs
- **THEN** files in storage without database reference are identified
- **AND** files older than retention period (90 days configurable) are deleted

#### Scenario: Cleanup expired draft files
- **WHEN** draft response expires
- **THEN** associated uploaded files are deleted
- **AND** storage space is freed

## MODIFIED Requirements

None - This is a new field type addition to existing field types.
