# OpenSpec Change: Enhance File Storage and Section Branching UI

**Status**: Draft - Ready for Review  
**Created**: 2025-11-01  
**Change ID**: `enhance-file-storage-and-branching-ui`

## Overview

This proposal enhances the survey system with two major features:

1. **Flexible File Storage**: Support for local and Google Drive storage backends with clickable URLs in CSV exports
2. **Inline Branching Configuration**: User-friendly interface to configure section branching directly in question creation UI

## Quick Links

- **[proposal.md](./proposal.md)** - Why this change is needed and what it includes
- **[tasks.md](./tasks.md)** - Detailed implementation checklist (~170 tasks, 3-4 weeks)
- **[design.md](./design.md)** - Technical architecture and design decisions
- **[Spec Deltas](./specs/)** - Requirements changes for affected capabilities

## Key Features

### Part 1: File Storage Enhancements

- ✅ Multiple storage backends (Local filesystem + Google Drive)
- ✅ Storage configuration UI in admin interface
- ✅ OAuth2 authentication for Google Drive
- ✅ Clickable file URLs in CSV exports (instead of file paths)
- ✅ Survey-specific export directories with timestamps
- ✅ Automatic fallback to local storage on errors

### Part 2: Section Branching UI

- ✅ "Enable branching" toggle in question form (for radio questions)
- ✅ Dropdown selectors to map each radio option to target section
- ✅ Visual preview of branching flow
- ✅ Backward compatible with existing section-level branching rules
- ✅ Question-level branching takes priority over section rules

### Part 3: Enhanced Exports

- ✅ CSV includes "File URL" column for file upload questions
- ✅ URLs work for both local and Google Drive files
- ✅ Export filenames include timestamp
- ✅ Optional: Bundle uploaded files with CSV in ZIP archive

## Validation Status

✅ **PASSED**: Strict OpenSpec validation

```bash
$ openspec validate enhance-file-storage-and-branching-ui --strict
Change 'enhance-file-storage-and-branching-ui' is valid
```

## Implementation Summary

### Complexity
- **Estimated Effort**: 3-4 weeks (1 developer full-time)
- **Total Tasks**: ~170 tasks broken down across 9 phases
- **Risk Level**: Medium (Google Drive API integration, OAuth2)

### Dependencies
```
google-auth==2.27.0
google-auth-oauthlib==1.2.0
google-api-python-client==2.115.0
django-encrypted-model-fields==0.6.5
```

### Database Changes
- New model: `StorageConfiguration`
- Add field: `Answer.file_url` (URLField)
- Add field: `Question.enable_branching` (BooleanField)
- Add field: `Question.branch_config` (JSONField)

## Architecture Highlights

### Storage System
```
Survey View → Storage Manager → Storage Backend (Local/Google Drive)
```

**Key Components**:
- `StorageBackend` (abstract interface)
- `LocalStorageBackend` (filesystem + absolute URLs)
- `GoogleDriveBackend` (Google Drive API + OAuth2)
- `StorageManager` (factory, caching, fallback logic)

### Branching System
```
User Submits → Branch Evaluator → Question Branching → Section Rules → Next Section
```

**Key Components**:
- Question-level: `enable_branching` flag + `branch_config` JSON
- Section-level: Existing `BranchRule` model (backward compatible)
- Evaluation: `BranchEvaluator` class with precedence logic

## Use Cases

### Use Case 1: Store Files in Google Drive
**As a** survey administrator  
**I want to** configure Google Drive as the storage backend  
**So that** uploaded files are automatically backed up to the cloud

### Use Case 2: Export with File URLs
**As a** survey administrator  
**I want to** export responses with clickable file URLs  
**So that** I can easily access uploaded documents from the CSV

### Use Case 3: Configure Branching in Question Form
**As a** survey administrator  
**I want to** set up branching directly when creating a question  
**So that** I don't need to configure branching separately in section settings

## Breaking Changes

**None** - This is a fully backward-compatible enhancement:
- Existing local file storage continues to work (default)
- Existing section-level branching rules remain functional
- New features are opt-in (must be configured/enabled)
- Database migrations are additive only

## Next Steps

1. **Review**: Get stakeholder approval on proposal
2. **Planning**: Prioritize and schedule implementation
3. **Implementation**: Follow tasks.md checklist
4. **Testing**: Run unit, integration, and E2E tests
5. **Documentation**: Update admin guides and user docs
6. **Deployment**: Roll out with monitoring

## Related Work

- **`file-upload-storage-options`**: Similar storage backend work (consider merging)
- **`improve-survey-ui-fileupload`**: Core file upload UI (already completed)
- **`enhance-multisession-survey-ui`**: Survey builder improvements (mostly complete)
- **`add-sections-branching-fileupload`**: Original sections/branching work (archived)

## Questions or Feedback?

For questions about this proposal, please:
1. Review the detailed docs: `proposal.md`, `design.md`, `tasks.md`
2. Check spec deltas in `specs/` directory
3. Contact the development team

---

**Created by**: AI Assistant  
**Last Updated**: 2025-11-01  
**OpenSpec Version**: Compliant with current spec format
