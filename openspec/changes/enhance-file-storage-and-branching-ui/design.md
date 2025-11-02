# Technical Design: Enhance File Storage and Section Branching UI

**Change ID**: `enhance-file-storage-and-branching-ui`

## Goals

1. Enable flexible file storage with local and Google Drive backends
2. Add clickable file URLs to CSV exports
3. Add inline branching configuration to question creation UI
4. Organize exports in survey-specific directories

## Non-Goals

- Other cloud providers (AWS S3, Azure) - future work
- Visual flowchart builder - separate proposal
- File encryption - separate security feature
- Bulk migration tools - manual process acceptable for v1

## Architecture

### Storage System

```
Survey View → Storage Manager → Storage Backend (Local/Google Drive)
```

**Components**:
- `StorageBackend` (abstract): Interface with save(), get_url(), delete(), exists(), test_connection()
- `LocalStorageBackend`: Filesystem storage with absolute URL generation
- `GoogleDriveBackend`: Google Drive API with OAuth2
- `StorageManager`: Factory pattern, caching, fallback to local
- `StorageConfiguration`: Model to persist settings (encrypted credentials)

### Branching System

```
User Submits → Branch Evaluator → Checks Question Branching → Falls back to Section Rules → Next Section
```

**Components**:
- `Question.enable_branching`: Boolean flag
- `Question.branch_config`: JSON mapping choices to section IDs
- `BranchEvaluator`: Evaluates branching with priority (question > section > default)
- Question form UI: Toggle + section selectors + preview

## Database Changes

```sql
-- New table
CREATE TABLE djf_surveys_storageconfiguration (
    id INTEGER PRIMARY KEY,
    provider VARCHAR(20),  -- 'local' or 'google_drive'
    credentials TEXT,      -- Encrypted JSON
    config TEXT,           -- JSON settings
    is_active BOOLEAN,
    created_at DATETIME,
    updated_at DATETIME
);

-- Add columns
ALTER TABLE djf_surveys_answer ADD COLUMN file_url VARCHAR(500);
ALTER TABLE djf_surveys_question ADD COLUMN enable_branching BOOLEAN DEFAULT 0;
ALTER TABLE djf_surveys_question ADD COLUMN branch_config TEXT DEFAULT '{}';
```

## Security

1. **Credentials**: Encrypt OAuth tokens using `django-encrypted-model-fields`
2. **File Access**: Google Drive files set to "anyone with link", local files through Django views
3. **OAuth Flow**: Use state parameter for CSRF protection
4. **Input Validation**: Validate branch targets, sanitize filenames

## Performance

1. Cache storage backend instance (5 min TTL)
2. Cache Google Drive folder IDs (in-memory dict)
3. Index on `enable_branching` field
4. Stream large file uploads

## Error Handling

- Storage failures → Fallback to local storage + log error
- Branch target not found → Continue to next section
- Google API quota exceeded → Retry with backoff

## Testing

- Unit tests for each storage backend (mock Google API)
- Integration test for OAuth flow (test account)
- E2E test: Upload → Storage → Export → Download
- E2E test: Survey with branching → Submit → Navigation

## Deployment

1. Add env vars: GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, ENCRYPTION_KEY
2. Run migrations
3. Install: google-auth, google-api-python-client, django-encrypted-model-fields
4. Configure default storage
5. Test uploads and exports

## Risks & Mitigation

| Risk | Mitigation |
|------|------------|
| Google API quota | Rate limiting, clear errors |
| Token expiration | Auto-refresh logic |
| Large file uploads | Stream uploads, progress indicators |
| Complex branching UI | Keep simple, optional toggle |

See `tasks.md` for detailed implementation steps.
