# Proposal: Enhance File Storage and Section Branching UI

**Change ID**: `enhance-file-storage-and-branching-ui`  
**Status**: Draft  
**Created**: 2025-11-01  
**Author**: System

## Why

The survey system currently has two significant limitations that impact administrator workflow and data management:

1. **File Storage Limitations**: Uploaded files are only saved locally with no cloud backup option, and CSV exports show file paths instead of accessible download links, making it difficult to access and share uploaded documents.

2. **Limited Branching Configuration**: While radio questions support conditional branching to different sections, this feature is not exposed in the question creation/editing interface, requiring administrators to configure branching separately in the section settings.

These limitations reduce efficiency for survey administrators and make it harder to create sophisticated survey flows and manage uploaded data.

## What Changes

### Part 1: File Upload Storage & Export Enhancements

- **Multiple Storage Backends**: Add support for both local storage (existing) and Google Drive cloud storage
- **Storage Configuration UI**: New admin interface to configure and switch between storage providers
- **Google Drive Integration**: OAuth2 authentication and automatic folder organization
- **Enhanced CSV Export**: Include clickable download URLs instead of file paths in exported reports
- **Per-Survey Export Organization**: Organize exported files in survey-specific directories with timestamped exports
- **File URL Generation**: Generate accessible URLs for both local files and Google Drive files

### Part 2: Section Branching UI in Question Interface

- **Inline Branching Configuration**: Add branching settings directly to the question creation/editing modal
- **Toggle-able Feature**: Optional checkbox to enable section branching for radio questions
- **Visual Section Selector**: Dropdown to select target section for each radio option
- **User-Friendly Interface**: Simplified UI for administrators and non-admin users with edit permissions
- **Preview Branching Flow**: Show visual indicator of configured branching logic

### Part 3: Optimized Report Export Structure

- **Survey-Specific Directories**: Create separate export folders per survey
- **Timestamped Exports**: Include timestamp in export filenames
- **File Attachments**: Optionally bundle uploaded files with CSV export
- **Export History**: Track export operations with metadata

## Impact

### Affected Components

**Models**:
- New: `StorageConfiguration` - Store storage backend settings
- Modified: `Answer` - Add `file_url` field for accessible URLs
- Modified: `Question` - Add `enable_branching` field for inline branching toggle

**Views**:
- New: `StorageSettingsView` - Configure storage backends
- New: `GoogleDriveAuthView` - Handle OAuth2 flow
- Modified: `DownloadResponseSurveyView` - Generate URLs in CSV export
- Modified: `AdminQuestionFormView` - Add branching configuration UI
- Modified: `CreateSurveyFormView` - Use new storage manager

**Templates**:
- New: `storage_settings.html` - Storage configuration page
- Modified: `question_form.html` - Add branching section
- Modified: `admin_download.html` - Export options UI

**New Modules**:
- `djf_surveys/storage/` - Storage backend framework
  - `base.py` - Abstract storage interface
  - `local.py` - Local filesystem backend
  - `google_drive.py` - Google Drive backend
  - `manager.py` - Storage manager

### Breaking Changes

**None** - This is a backward-compatible enhancement:
- Existing local file storage continues to work
- Existing branching configuration through section rules remains functional
- New features are opt-in (storage must be configured, branching must be enabled)
- Database migrations are additive only

### Migration Path

1. **Phase 1**: Deploy code with default local storage (no configuration needed)
2. **Phase 2**: Administrators can optionally configure Google Drive
3. **Phase 3**: Administrators can enable inline branching for specific questions
4. **Phase 4**: Existing files remain accessible, new uploads use configured storage

## Affected Specs

This change affects the following capabilities:

- `openspec/specs/survey-field-types/` - Add file storage configuration
- `openspec/specs/survey-branch-logic/` - Add inline branching UI
- `openspec/specs/survey-data-export/` - Add file URLs to exports (NEW)

## Dependencies

### Python Packages
```
google-auth==2.27.0
google-auth-oauthlib==1.2.0
google-api-python-client==2.115.0
django-encrypted-model-fields==0.6.5
```

### External Services
- Google Cloud Platform project (optional, for Google Drive)
- Google Drive API enabled (optional)
- OAuth2 credentials (optional)

### Database Migrations
- Add `StorageConfiguration` model
- Add `Answer.file_url` field
- Add `Question.enable_branching` field
- Add `Question.branch_config` JSONField

## Success Criteria

### File Storage
1. ✅ Administrators can configure storage backend (Local/Google Drive)
2. ✅ Files upload to configured storage location
3. ✅ CSV exports include clickable file URLs
4. ✅ Google Drive files have shareable links
5. ✅ Local files generate full accessible URLs
6. ✅ Storage settings persist and can be changed
7. ✅ Test connection before saving settings
8. ✅ Error handling for storage failures

### Branching UI
1. ✅ "Enable Branching" toggle visible in question form for radio type
2. ✅ Section selector appears when branching is enabled
3. ✅ Each radio option can be mapped to a target section
4. ✅ Branching configuration saves correctly
5. ✅ Visual preview of branching flow
6. ✅ Backward compatible with existing section-level rules
7. ✅ Toggle can be turned off to disable feature

### Report Export
1. ✅ Exports organized in survey-specific folders
2. ✅ Export filenames include timestamp
3. ✅ CSV includes "File URL" column for file upload questions
4. ✅ URLs are clickable and download files
5. ✅ Export history tracked in admin interface

## Timeline

**Estimated Duration**: 3-4 weeks

- **Week 1**: Storage abstraction layer and local backend
- **Week 2**: Google Drive integration and OAuth2 flow
- **Week 3**: Enhanced CSV export with file URLs
- **Week 4**: Branching UI and testing

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Google API quota limits | Medium | Implement rate limiting, clear error messages |
| OAuth token expiration | Low | Auto-refresh tokens, provide re-auth flow |
| Large file uploads to Google Drive | Medium | Show progress indicators, handle timeouts |
| Branching UI complexity | Low | Keep UI simple with optional toggle |
| Export file size with attachments | Medium | Make file bundling optional |

## Out of Scope

- Other cloud providers (AWS S3, Azure, Dropbox) - future enhancement
- File encryption at rest - separate security feature
- Visual flowchart builder for branching - covered by existing proposal
- Bulk file migration tool - can be done manually
- File versioning - separate feature
- Advanced branching conditions beyond radio selection

## Related Proposals

- **`file-upload-storage-options`**: Similar storage backend work (can merge/supersede)
- **`improve-survey-ui-fileupload`**: Core file upload UI (already completed)
- **`enhance-multisession-survey-ui`**: Survey builder improvements (completed)
- **`add-sections-branching-fileupload`**: Original sections and branching work (archived)

## Open Questions

1. Should we merge this with existing `file-upload-storage-options` proposal?
2. Should branching configuration be per-question or remain per-section only?
3. What should the default behavior be when branching is not configured?
4. Should we provide a migration script for existing local files to Google Drive?
5. How should we handle file size limits for Google Drive (free vs paid accounts)?

## Next Steps

1. **Review and Approval**: Get stakeholder feedback on proposal
2. **Spec Deltas**: Create detailed spec deltas for affected capabilities
3. **Design Doc**: Create technical design document
4. **Tasks**: Break down into implementation tasks
5. **Validation**: Run `openspec validate enhance-file-storage-and-branching-ui --strict`
