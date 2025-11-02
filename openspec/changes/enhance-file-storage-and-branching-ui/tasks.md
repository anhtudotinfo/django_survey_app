# Implementation Tasks: Enhance File Storage and Section Branching UI

**Change ID**: `enhance-file-storage-and-branching-ui`

---

## Part 1: File Storage Enhancements

### Phase 1.1: Storage Backend Framework (Week 1)

#### 1.1.1 Create Storage Module Structure
- [ ] Create `djf_surveys/storage/` directory
- [ ] Create `djf_surveys/storage/__init__.py`
- [ ] Create `djf_surveys/storage/base.py` with abstract `StorageBackend` class
- [ ] Define interface methods: `save()`, `get_url()`, `delete()`, `exists()`, `test_connection()`
- [ ] Add exception classes: `StorageError`, `ConnectionError`, `UploadError`

#### 1.1.2 Implement Local Storage Backend
- [ ] Create `djf_surveys/storage/local.py`
- [ ] Implement `LocalStorageBackend` class extending `StorageBackend`
- [ ] Use Django's `FileSystemStorage`
- [ ] Implement `save()` method with configurable subdirectory
- [ ] Implement `get_url()` to generate full absolute URLs
- [ ] Implement `delete()` method
- [ ] Implement `exists()` method
- [ ] Implement `test_connection()` to verify directory is writable
- [ ] Handle filename conflicts with timestamp suffix

#### 1.1.3 Create Storage Configuration Model
- [ ] Create migration for `StorageConfiguration` model
- [ ] Add fields: `provider` (CharField), `credentials` (EncryptedJSONField), `config` (JSONField), `is_active` (BooleanField)
- [ ] Add `created_at` and `updated_at` timestamps
- [ ] Implement `save()` to ensure only one active configuration
- [ ] Add `get_active()` class method
- [ ] Add `test_connection()` method
- [ ] Add validation in `clean()` method
- [ ] Install `django-encrypted-model-fields==0.6.5` or similar
- [ ] Configure encryption key in settings

#### 1.1.4 Create Storage Manager
- [ ] Create `djf_surveys/storage/manager.py`
- [ ] Implement `StorageManager` class
- [ ] Add `get_backend()` method with caching (5 min cache timeout)
- [ ] Add `_create_backend()` private method for factory pattern
- [ ] Add `clear_cache()` method
- [ ] Add convenience methods: `save_file()`, `get_file_url()`, `delete_file()`
- [ ] Implement fallback to local storage if configured storage fails
- [ ] Add logging for storage operations

### Phase 1.2: Google Drive Integration (Week 2)

#### 1.2.1 Setup Dependencies
- [ ] Add `google-auth==2.27.0` to `requirements.txt`
- [ ] Add `google-auth-oauthlib==1.2.0` to `requirements.txt`
- [ ] Add `google-api-python-client==2.115.0` to `requirements.txt`
- [ ] Update virtual environment: `pip install -r requirements.txt`
- [ ] Create Google Cloud project documentation in `GOOGLE_DRIVE_SETUP.md`
- [ ] Document OAuth2 credential creation steps

#### 1.2.2 Implement Google Drive Backend
- [ ] Create `djf_surveys/storage/google_drive.py`
- [ ] Implement `GoogleDriveBackend` class extending `StorageBackend`
- [ ] Add `SCOPES = ['https://www.googleapis.com/auth/drive.file']`
- [ ] Implement `__init__()` to initialize credentials and service
- [ ] Implement `_get_or_create_folder()` helper with path parsing
- [ ] Implement folder caching in `self.folder_cache`
- [ ] Implement `save()` method to upload file to Drive
- [ ] Set file permissions to "anyone with link can view"
- [ ] Implement `get_url()` to return shareable link
- [ ] Implement `delete()` method
- [ ] Implement `exists()` method
- [ ] Implement `test_connection()` to verify API access
- [ ] Add retry logic with exponential backoff for API calls
- [ ] Handle Google Drive API errors gracefully

#### 1.2.3 OAuth2 Flow Views
- [ ] Create `djf_surveys/admins/storage_views.py`
- [ ] Implement `GoogleDriveAuthView` to initiate OAuth flow
- [ ] Generate authorization URL with correct scopes
- [ ] Store state parameter in session for CSRF protection
- [ ] Implement `GoogleDriveCallbackView` to handle OAuth callback
- [ ] Validate state parameter
- [ ] Exchange authorization code for tokens
- [ ] Store tokens in `StorageConfiguration.credentials` (encrypted)
- [ ] Add `@staff_member_required` decorator
- [ ] Display success/error messages
- [ ] Add URL routes in `djf_surveys/admins/urls.py`

### Phase 1.3: Storage Configuration UI (Week 2-3)

#### 1.3.1 Storage Settings Page Template
- [ ] Create template `djf_surveys/templates/djf_surveys/admins/storage_settings.html`
- [ ] Extend base admin template
- [ ] Add page title "Storage Configuration"
- [ ] Add provider selection radio buttons: Local Storage / Google Drive
- [ ] Add local storage path input field (shown only for Local)
- [ ] Add "Connect Google Drive" button (shown only for Google Drive)
- [ ] Add "Test Connection" button
- [ ] Add "Save Settings" button
- [ ] Display current storage status indicator (green/red)
- [ ] Display connected Google account email (if applicable)
- [ ] Add "Disconnect" button for Google Drive
- [ ] Style with Tailwind CSS classes
- [ ] Add JavaScript for dynamic form behavior

#### 1.3.2 Storage Settings View
- [ ] Create `StorageSettingsView` in `storage_views.py`
- [ ] Extend `TemplateView` or `FormView`
- [ ] Add `@staff_member_required` decorator
- [ ] Handle GET request: display current configuration
- [ ] Handle POST request: save configuration
- [ ] Add form validation
- [ ] Call `test_connection()` before saving
- [ ] Show success/error messages
- [ ] Clear storage manager cache on save
- [ ] Add URL route: `/dashboard/settings/storage/`

#### 1.3.3 Storage Configuration Form
- [ ] Create `StorageConfigurationForm` in `djf_surveys/admins/forms.py` or `v2/forms.py`
- [ ] Add `provider` choice field (Local/Google Drive)
- [ ] Add `local_path` CharField (optional, for local storage)
- [ ] Add validation for local path (must be valid directory)
- [ ] Add `clean()` method for cross-field validation
- [ ] Add help text for each field

#### 1.3.4 Navigation Integration
- [ ] Add "Storage Settings" link to admin navigation menu
- [ ] Add icon (e.g., `bi-cloud-upload` or `bi-hdd`)
- [ ] Place in Settings or Configuration section
- [ ] Ensure only visible to staff users

### Phase 1.4: File Upload Integration (Week 3)

#### 1.4.1 Update File Upload Views
- [ ] Modify survey submission view to use `StorageManager`
- [ ] Replace `file.save()` with `StorageManager.save_file(file, path)`
- [ ] Generate path: `survey_{id}/question_{id}/{filename}`
- [ ] Store returned URL in `Answer.file_url` field
- [ ] Keep `Answer.value` for backward compatibility (store storage path)
- [ ] Handle storage errors with user-friendly messages
- [ ] Add file upload progress indicator (optional)
- [ ] Update success messages

#### 1.4.2 Update Answer Model
- [ ] Create migration to add `file_url` field to `Answer` model
- [ ] Add `file_url = models.URLField(max_length=500, blank=True, null=True)`
- [ ] Update `save()` method to populate `file_url` when file is uploaded
- [ ] Add `get_file_url()` method that returns `file_url` if available, else generates from `value`
- [ ] Update `get_value_for_csv` property to return URL instead of path
- [ ] Run migration: `python manage.py migrate`

#### 1.4.3 Update File Display in Admin
- [ ] Update answer list template to show clickable file URLs
- [ ] Format as `<a href="{url}" target="_blank">📎 {filename}</a>`
- [ ] Update file download view to redirect to `file_url` if available
- [ ] Add file preview for images (show thumbnail)
- [ ] Handle missing files gracefully (show "File not found" message)

### Phase 1.5: Enhanced CSV Export (Week 3)

#### 1.5.1 Modify CSV Export Logic
- [ ] Update `DownloadResponseSurveyView.get()` method
- [ ] Add "File URL" column header for file upload questions
- [ ] For each file upload answer, include `answer.get_file_url()` in CSV
- [ ] Generate full absolute URLs for local files using `request.build_absolute_uri()`
- [ ] For Google Drive files, use stored shareable link from `file_url`
- [ ] Handle multiple files if question allows (comma-separated URLs)
- [ ] Handle missing files (empty cell or "No file")

#### 1.5.2 Optimize Export File Structure
- [ ] Create survey-specific export directory: `exports/{survey_slug}/`
- [ ] Generate timestamped filename: `{survey_slug}_{YYYY-MM-DD_HH-MM-SS}.csv`
- [ ] Ensure export directory exists (create if needed)
- [ ] Save export metadata: timestamp, user, file size
- [ ] Add option to bundle uploaded files with CSV (zip archive)
- [ ] Update export template with new options

#### 1.5.3 Export Options UI
- [ ] Update export page template
- [ ] Add checkbox: "Include file download URLs" (checked by default)
- [ ] Add checkbox: "Bundle uploaded files (ZIP)" (optional)
- [ ] Add dropdown: "Export format" (CSV/Excel - future)
- [ ] Update export view to handle options
- [ ] Generate ZIP archive if "Bundle files" is selected

---

## Part 2: Section Branching UI Enhancements

### Phase 2.1: Question Model Updates (Week 3)

#### 2.1.1 Add Branching Fields to Question Model
- [ ] Create migration to add `enable_branching` field to `Question` model
- [ ] Add `enable_branching = models.BooleanField(default=False)`
- [ ] Add `branch_config = models.JSONField(default=dict, blank=True)`
- [ ] Structure of `branch_config`: `{"option1": section_id, "option2": section_id, ...}`
- [ ] Run migration: `python manage.py migrate`

#### 2.1.2 Add Model Methods
- [ ] Add `get_branch_target(option_value)` method to return target section ID
- [ ] Add `set_branch_target(option_value, section_id)` method
- [ ] Add `has_branching_configured()` property
- [ ] Add validation in `clean()` to ensure branch targets are valid sections in same survey

### Phase 2.2: Question Form UI Updates (Week 3-4)

#### 2.2.1 Update Question Form Template
- [ ] Modify `djf_surveys/templates/djf_surveys/admins/question_form.html`
- [ ] Add "Section Branching" section below field type and choices
- [ ] Add toggle checkbox: "Enable section branching for this question"
- [ ] Add JavaScript to show/hide branching configuration when toggled
- [ ] Add JavaScript to show branching config only for radio type questions

#### 2.2.2 Add Branching Configuration UI
- [ ] Add container div for branching configuration (hidden by default)
- [ ] For each radio choice, add section selector dropdown
- [ ] Populate section dropdown with sections from current survey
- [ ] Add option: "(Continue to next section)" as default
- [ ] Add option: "(End survey)" to end survey after this question
- [ ] Label each dropdown with the choice text
- [ ] Update dynamically when choices field changes

#### 2.2.3 Add Visual Preview
- [ ] Add collapsible "Preview Branching Flow" section
- [ ] Show simple flowchart: Question → Option 1 → Section A, Option 2 → Section B, etc.
- [ ] Use arrows or lines to visualize flow
- [ ] Highlight which sections are targets
- [ ] Update preview when branching config changes

#### 2.2.4 Add JavaScript Logic
- [ ] Add event listener for "Enable branching" checkbox toggle
- [ ] Add event listener for field type change (show only for radio)
- [ ] Add event listener for choices field change (update option dropdowns)
- [ ] Validate that all options have branch targets before save
- [ ] Show warning if branching is enabled but no targets configured
- [ ] Add function to sync choices with branch config dropdowns

### Phase 2.3: Question Form View Updates (Week 4)

#### 2.3.1 Update Question Form View
- [ ] Modify `AdminQuestionFormView` or equivalent
- [ ] Add `enable_branching` field to form
- [ ] Add `branch_config` field (can be hidden, populated via JS)
- [ ] Add context data: available sections for current survey
- [ ] Handle save: parse branch config from form data
- [ ] Validate branch targets are valid section IDs
- [ ] Update success message to mention branching if enabled

#### 2.3.2 Create Question Form Class
- [ ] Create or update `QuestionForm` in `djf_surveys/forms.py` or `admins/forms.py`
- [ ] Add `enable_branching` BooleanField
- [ ] Add custom widget for `branch_config` (HiddenInput or custom JSON widget)
- [ ] Add `clean_branch_config()` method to validate JSON structure
- [ ] Ensure branch targets reference valid sections in same survey
- [ ] Add help text for branching fields

### Phase 2.4: Integration with Existing Branch Logic (Week 4)

#### 2.4.1 Update Branch Evaluator
- [ ] Modify `djf_surveys/branch_logic.py` or create if doesn't exist
- [ ] Update `BranchEvaluator` to check question-level branching first
- [ ] If `question.enable_branching` is True, use `question.branch_config`
- [ ] Fall back to section-level `BranchRule` if question branching not configured
- [ ] Ensure priority: question-level branching > section-level rules
- [ ] Add logging for branch evaluation

#### 2.4.2 Update Navigation Logic
- [ ] Modify `djf_surveys/navigation.py` or survey form view
- [ ] When user submits section, evaluate question-level branching
- [ ] Get answer value for radio questions with branching enabled
- [ ] Look up target section from `branch_config`
- [ ] Navigate to target section or end survey
- [ ] Log branching decisions for debugging

#### 2.4.3 Backward Compatibility
- [ ] Ensure existing section-level `BranchRule` objects still work
- [ ] Test surveys without question-level branching still work
- [ ] Test surveys with mixed (some questions with branching, some without)
- [ ] Document precedence: question branching > section rules

### Phase 2.5: Admin Interface for Branching (Week 4)

#### 2.5.1 Update Question List View
- [ ] Add column: "Branching" with icon if enabled
- [ ] Show tooltip: "This question has section branching configured"
- [ ] Add filter: "Has branching" to filter questions with branching enabled

#### 2.5.2 Update Survey Preview
- [ ] Show branching indicator in survey preview
- [ ] Display branch targets below question in preview
- [ ] Format: "Option A → Section 2, Option B → Section 3"

#### 2.5.3 Add Validation Warnings
- [ ] Check for circular branching (Section A → B → A)
- [ ] Warn if branch target section doesn't exist
- [ ] Warn if branching is enabled but no targets configured
- [ ] Show warnings in admin interface

---

## Part 3: Testing & Documentation

### Phase 3.1: Unit Tests (Week 4)

#### 3.1.1 Storage Backend Tests
- [ ] Test `LocalStorageBackend.save()`, `get_url()`, `delete()`, `exists()`, `test_connection()`
- [ ] Test `GoogleDriveBackend` methods with mocked API responses
- [ ] Test `StorageManager.get_backend()` with different configurations
- [ ] Test fallback to local storage on errors
- [ ] Test credential encryption/decryption
- [ ] Test storage configuration model validation

#### 3.1.2 Branching Logic Tests
- [ ] Test question-level branching evaluation
- [ ] Test precedence: question branching > section rules
- [ ] Test backward compatibility with existing section rules
- [ ] Test branching with different answer values
- [ ] Test "End survey" branching
- [ ] Test invalid branch target handling

#### 3.1.3 CSV Export Tests
- [ ] Test CSV export with local file URLs
- [ ] Test CSV export with Google Drive URLs
- [ ] Test export with missing files
- [ ] Test export filename and directory structure
- [ ] Test export options (include URLs, bundle files)

### Phase 3.2: Integration Tests (Week 4)

#### 3.2.1 End-to-End Storage Tests
- [ ] Test OAuth2 flow with test Google account
- [ ] Test file upload to local storage
- [ ] Test file upload to Google Drive
- [ ] Test switching storage providers
- [ ] Test CSV export with file URLs
- [ ] Test file access through generated URLs

#### 3.2.2 End-to-End Branching Tests
- [ ] Create test survey with question-level branching
- [ ] Submit survey and verify navigation
- [ ] Test branching to different sections
- [ ] Test "End survey" branching
- [ ] Test with multiple branching questions in sequence
- [ ] Test mixed survey (some questions with branching, some without)

### Phase 3.3: User Acceptance Testing

#### 3.3.1 Storage Configuration Testing
- [ ] Admin configures local storage (default)
- [ ] Admin configures Google Drive storage
- [ ] Admin tests connection before saving
- [ ] Admin switches between storage providers
- [ ] Admin disconnects Google Drive

#### 3.3.2 File Upload Testing
- [ ] User uploads file in survey
- [ ] File saves to configured storage
- [ ] Admin views uploaded files in admin interface
- [ ] Admin exports CSV with file URLs
- [ ] Admin clicks URL and downloads file

#### 3.3.3 Branching UI Testing
- [ ] Admin creates radio question
- [ ] Admin enables branching
- [ ] Admin configures branch targets for each option
- [ ] Admin previews branching flow
- [ ] Admin saves question
- [ ] User takes survey and branching works correctly

### Phase 3.4: Documentation (Week 4)

#### 3.4.1 User Documentation
- [ ] Create `STORAGE_CONFIGURATION.md` with setup instructions
- [ ] Document Google Cloud project setup
- [ ] Document OAuth2 credential creation
- [ ] Add screenshots of storage settings page
- [ ] Document how to switch storage providers
- [ ] Document CSV export enhancements

#### 3.4.2 Admin Documentation
- [ ] Update `ADMIN_GUIDE.md` with storage configuration section
- [ ] Add section on question-level branching
- [ ] Document branching precedence (question > section)
- [ ] Add examples and best practices
- [ ] Document export organization and file URLs

#### 3.4.3 Developer Documentation
- [ ] Document storage backend interface
- [ ] Document how to add new storage providers
- [ ] Document branching evaluation logic
- [ ] Add code examples
- [ ] Document configuration options
- [ ] Update API documentation

#### 3.4.4 Migration Guide
- [ ] Document migrating from local to Google Drive
- [ ] Provide migration script for existing files (optional)
- [ ] Document rollback procedure
- [ ] Document backup recommendations
- [ ] Update deployment documentation

---

## Phase 4: Deployment & Monitoring

### Phase 4.1: Deployment Preparation

- [ ] Add environment variables to `.env.example`
- [ ] Update deployment documentation
- [ ] Prepare production Google OAuth credentials (if using)
- [ ] Test migrations in staging environment
- [ ] Run security audit on storage implementation

### Phase 4.2: Production Deployment

- [ ] Run database migrations
- [ ] Deploy code to production
- [ ] Configure default storage (local)
- [ ] Test file upload functionality
- [ ] Test CSV export with file URLs
- [ ] Configure Google Drive (if desired)
- [ ] Monitor logs for errors

### Phase 4.3: Monitoring & Alerts

- [ ] Add logging for storage operations
- [ ] Track upload success/failure rates
- [ ] Monitor Google Drive API quota usage (if applicable)
- [ ] Set up alerts for storage errors
- [ ] Track CSV export usage
- [ ] Monitor branching evaluation performance

---

## Task Summary

**Total Tasks**: ~170 tasks  
**Estimated Duration**: 3-4 weeks (1 developer full-time)

### By Part:
- **Part 1 (Storage)**: ~100 tasks, 2.5 weeks
  - Phase 1.1: Storage Framework (20 tasks, 2 days)
  - Phase 1.2: Google Drive (25 tasks, 4 days)
  - Phase 1.3: Configuration UI (20 tasks, 3 days)
  - Phase 1.4: Upload Integration (10 tasks, 1 day)
  - Phase 1.5: CSV Export (15 tasks, 2 days)

- **Part 2 (Branching UI)**: ~40 tasks, 1 week
  - Phase 2.1: Model Updates (8 tasks, 1 day)
  - Phase 2.2: Form UI (15 tasks, 2 days)
  - Phase 2.3: Form View (8 tasks, 1 day)
  - Phase 2.4: Integration (8 tasks, 1 day)
  - Phase 2.5: Admin Interface (5 tasks, 1 day)

- **Part 3 (Testing & Docs)**: ~30 tasks, 4 days
  - Phase 3.1: Unit Tests (15 tasks, 2 days)
  - Phase 3.2: Integration Tests (8 tasks, 1 day)
  - Phase 3.3: UAT (5 tasks, 0.5 day)
  - Phase 3.4: Documentation (12 tasks, 1.5 days)

**Priority**: Medium-High  
**Complexity**: High (Google Drive integration, OAuth2)  
**Risk**: Medium (external API dependencies)
