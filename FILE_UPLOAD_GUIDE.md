# Survey File Upload Guide

## Overview

The survey system supports file uploads as a question type, allowing users to submit documents, images, and other files as part of their survey responses.

## Features

- **Multiple File Types**: Support for images, PDFs, documents
- **Security**: File type validation, size limits, sanitized filenames
- **Access Control**: Files only accessible to authorized users
- **Organized Storage**: Files stored by survey and response
- **Cleanup**: Automatic cleanup of orphaned files

## Configuration

### Settings (moi/settings.py)

```python
# Media files configuration
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# File upload settings
SURVEY_FILE_UPLOAD_MAX_SIZE = 10 * 1024 * 1024  # 10 MB
SURVEY_FILE_ALLOWED_TYPES = [
    # Images
    'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp',
    # Documents
    'pdf', 'doc', 'docx', 'txt', 'rtf',
    # Spreadsheets
    'xls', 'xlsx', 'csv',
    # Other
    'zip', 'rar'
]
```

### Customization

To change allowed file types or size limits, update these settings:

```python
# Allow only images
SURVEY_FILE_ALLOWED_TYPES = ['jpg', 'jpeg', 'png', 'gif']

# Increase max size to 25 MB
SURVEY_FILE_UPLOAD_MAX_SIZE = 25 * 1024 * 1024

# Decrease max size to 5 MB
SURVEY_FILE_UPLOAD_MAX_SIZE = 5 * 1024 * 1024
```

## Creating File Upload Questions

### In Admin Interface

1. Go to **Admin → Surveys → [Your Survey] → Questions**
2. Click **Add Question**
3. Set **Type**: "File Upload"
4. Configure:
   - **Label**: Question text (e.g., "Upload your resume")
   - **Help Text**: Instructions (e.g., "PDF or DOC, max 10MB")
   - **Required**: Whether file is mandatory
   - **Section**: Which section this question belongs to

### Question Types

The file upload type is one of 11 available field types:
- Text
- Number
- Radio
- Select
- Multi Select
- Text Area
- URL
- Email
- Date
- Rating
- **File Upload** ← New type

## File Storage Structure

Files are organized by survey and response:

```
media/
└── survey_uploads/
    └── {survey_id}/
        └── {user_answer_id}/
            ├── document.pdf
            ├── image.jpg
            └── report.docx
```

Example:
```
media/survey_uploads/5/123/resume.pdf
media/survey_uploads/5/123/cover_letter.docx
media/survey_uploads/5/124/photo.jpg
```

## Security Features

### 1. File Type Validation

**Extension Check**: Verifies file extension is in allowed list

```python
# In validators.py
class FileTypeValidator:
    def __call__(self, file):
        ext = os.path.splitext(file.name)[1][1:].lower()
        if ext not in self.allowed_types:
            raise ValidationError('File type not allowed')
```

**MIME Type Verification**: Validates that file content matches extension

```python
# Prevents: uploading virus.exe renamed as virus.pdf
mime_type = mimetypes.guess_type(file.name)
if mime_type != expected_mime_type:
    raise ValidationError('File content does not match extension')
```

### 2. File Size Validation

```python
# In validators.py
class FileSizeValidator:
    def __call__(self, file):
        if file.size > self.max_size:
            raise ValidationError(f'File too large. Maximum: {max_mb} MB')
```

### 3. Filename Sanitization

```python
# In upload_survey_file()
from django.utils.text import get_valid_filename
clean_filename = get_valid_filename(filename)
```

Removes dangerous characters:
- Null bytes
- Path traversal attempts (../)
- Shell special characters
- Unicode exploits

### 4. Access Control

Files are served through a Django view with permission checks:

```python
# Only authorized users can download
@login_required
def download_file(request, answer_id):
    answer = get_object_or_404(Answer, id=answer_id)
    
    # Check permissions
    if not has_permission(request.user, answer):
        raise PermissionDenied
    
    # Serve file securely
    return FileResponse(answer.file_value)
```

### 5. URL Structure

Files are NOT directly accessible via MEDIA_URL. They must go through the view:

```
❌ BAD:  /media/survey_uploads/5/123/file.pdf (direct access)
✅ GOOD: /surveys/download/456/ (through permission check)
```

## User Experience

### Uploading Files

1. User sees file input field with help text
2. Selects file from device
3. Client-side validation (optional - file size/type)
4. Form submission uploads file
5. Server validates file
6. File saved to storage
7. Success confirmation shown

### Viewing Uploaded Files

In survey results/responses:
- Clickable file link: 📎 filename.pdf
- Clicking downloads file (with permission check)
- Shows "No file uploaded" if empty

### Error Messages

Clear user-friendly errors:
- "File type not allowed. Allowed types: pdf, doc, docx"
- "File too large. Maximum size: 10 MB"
- "File content does not match file extension"

## File Management

### Cleanup Commands

Two management commands handle file cleanup:

#### 1. Cleanup Orphaned Files

Removes files whose Answer records have been deleted:

```bash
python manage.py cleanup_orphaned_files
```

**What it does**:
- Scans all files in survey_uploads/
- Checks if corresponding Answer exists in database
- Deletes files with no matching Answer
- Reports count of deleted files

**When to run**: Daily via cron job

#### 2. Cleanup Expired Drafts

Removes draft responses past expiration:

```bash
python manage.py cleanup_expired_drafts
```

**What it does**:
- Finds DraftResponse records past expires_at date
- Deletes expired drafts
- Reports count of deleted drafts

**Note**: Draft responses don't store files directly (only final responses do)

**When to run**: Daily via cron job

### Automated Cleanup

Set up cron jobs for automatic cleanup:

```bash
# Edit crontab
crontab -e

# Add these lines:
# Daily at 2 AM - cleanup orphaned files
0 2 * * * cd /path/to/django_survey_app && source venv/bin/activate && python manage.py cleanup_orphaned_files >> /var/log/survey_cleanup.log 2>&1

# Daily at 2:30 AM - cleanup expired drafts
30 2 * * * cd /path/to/django_survey_app && source venv/bin/activate && python manage.py cleanup_expired_drafts >> /var/log/survey_cleanup.log 2>&1
```

See `CRON_SETUP.md` for detailed instructions.

### Manual File Deletion

Files are automatically deleted when:
1. Answer is deleted (via signal in models.py)
2. UserAnswer is deleted (cascades to Answer deletion)
3. Survey is deleted (cascades through relationships)

## Storage Backends

### Default: Local Filesystem

Files stored in `MEDIA_ROOT` directory:

```python
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
```

### Production: Cloud Storage (Optional)

For production, consider using cloud storage:

#### Amazon S3

```python
# Install: pip install django-storages boto3

# settings.py
INSTALLED_APPS += ['storages']

AWS_ACCESS_KEY_ID = 'your-key'
AWS_SECRET_ACCESS_KEY = 'your-secret'
AWS_STORAGE_BUCKET_NAME = 'your-bucket'
AWS_S3_REGION_NAME = 'us-east-1'

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
```

#### Google Cloud Storage

```python
# Install: pip install django-storages google-cloud-storage

# settings.py
DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
GS_BUCKET_NAME = 'your-bucket'
```

### Backup Strategy

**Local Storage**:
- Include `media/` in regular backups
- Backup database separately (contains file references)

**Cloud Storage**:
- Enable versioning on bucket
- Set up automated snapshots
- Configure lifecycle policies for old files

## Performance Considerations

### 1. File Size Impact

Large files increase:
- Upload time (user waiting)
- Storage costs
- Bandwidth usage
- Backup size

**Recommendation**: Keep max size reasonable (5-10 MB typical)

### 2. Storage Growth

Monitor storage usage:

```bash
# Check total storage used
du -sh media/survey_uploads/

# Check per-survey usage
du -sh media/survey_uploads/*/
```

### 3. Database Impact

File metadata stored in database:
- Answer.file_value (FileField)
- Path reference, not file content
- Minimal database impact

### 4. Serving Files

**Development**: Django serves files (slow)
**Production**: Use web server (Nginx/Apache) for better performance

```nginx
# Nginx configuration
location /media/ {
    alias /path/to/media/;
    
    # Internal only - don't allow direct access
    internal;
}
```

Then use X-Accel-Redirect in Django view for authenticated file serving.

## Troubleshooting

### File Upload Fails

**Check**:
1. MEDIA_ROOT exists and is writable
2. File size under limit
3. File type in allowed list
4. Disk space available

**Debug**:
```python
# In Django shell
from django.conf import settings
print(settings.MEDIA_ROOT)
print(settings.SURVEY_FILE_UPLOAD_MAX_SIZE)
print(settings.SURVEY_FILE_ALLOWED_TYPES)

import os
print(os.path.exists(settings.MEDIA_ROOT))
print(os.access(settings.MEDIA_ROOT, os.W_OK))
```

### File Not Found Error

**Possible Causes**:
1. File deleted from filesystem but Answer still exists
2. MEDIA_ROOT path changed
3. File moved/renamed manually

**Solution**: Run cleanup command to sync filesystem with database

### Permission Denied

**Check**:
1. File permissions (should be readable by web server user)
2. Directory permissions (755 typical)
3. User authentication and authorization

```bash
# Fix permissions
chmod 755 media/survey_uploads/
chmod 644 media/survey_uploads/**/**.pdf
```

### Disk Space Issues

**Monitor**:
```bash
# Check disk usage
df -h

# Find large files
find media/survey_uploads/ -type f -size +5M -ls
```

**Solutions**:
- Implement file retention policy
- Archive old surveys
- Move to cloud storage

## Testing

### Unit Tests

```python
# test_file_upload.py
def test_file_upload():
    # Create test file
    from django.core.files.uploadedfile import SimpleUploadedFile
    
    test_file = SimpleUploadedFile(
        "test.pdf",
        b"file content",
        content_type="application/pdf"
    )
    
    # Submit survey with file
    response = client.post(url, {
        'field_survey_1': test_file
    })
    
    assert response.status_code == 200
    assert Answer.objects.filter(file_value__isnull=False).exists()
```

### Manual Testing Checklist

- [ ] Upload allowed file types (PDF, images, docs)
- [ ] Try uploading disallowed type (should fail)
- [ ] Upload file larger than limit (should fail)
- [ ] Upload file just under limit (should succeed)
- [ ] Submit survey with file
- [ ] View response and verify file link
- [ ] Download file and verify content
- [ ] Delete response and verify file deleted
- [ ] Test with authenticated user
- [ ] Test with anonymous user (if allowed)
- [ ] Test draft save with file (files uploaded on final submit)

## Best Practices

### 1. Set Appropriate Limits
- **Images**: 2-5 MB usually sufficient
- **Documents**: 5-10 MB for typical PDFs
- **Large files**: Consider splitting into multiple questions or alternative approach

### 2. Clear Instructions
In help text, specify:
- Accepted file types
- Maximum file size
- Purpose of upload

Example: "Upload your resume (PDF or DOC, maximum 5MB)"

### 3. Handle Errors Gracefully
- Show clear error messages
- Preserve other form data on file upload error
- Provide retry option

### 4. Accessibility
- Use proper labels
- Provide alternative text
- Ensure keyboard navigation works

### 5. Monitor Storage
- Set up alerts for disk usage
- Regular cleanup of old surveys
- Archive strategy for completed surveys

### 6. Privacy & GDPR
- Include file uploads in data export
- Delete files when user requests data deletion
- Secure storage and access controls
- Retention policy documentation

## Integration with Other Features

### With Sections
- File upload questions work in any section
- Files uploaded when final survey submitted (not on section save)
- Draft system doesn't store files (only final responses)

### With Branch Logic
- Cannot branch based on file upload
- Branch on other questions, file upload can be in any branch

### With Draft System
- File inputs shown in draft forms
- Files only saved on final submission
- Resuming draft shows file input again (user must re-upload)

## Future Enhancements

Possible improvements:
- [ ] Multiple file uploads per question
- [ ] Image preview before upload
- [ ] Progress bar for large uploads
- [ ] Direct upload to cloud storage (bypass Django)
- [ ] Virus scanning integration
- [ ] Image resizing/optimization
- [ ] OCR for scanned documents
- [ ] File conversion (e.g., DOCX to PDF)

## See Also

- **Admin Guide**: `ADMIN_GUIDE.md` - Creating file upload questions
- **Security Review**: `SECURITY_REVIEW.md` - Security analysis
- **Cron Setup**: `CRON_SETUP.md` - Automated cleanup
- **Code**: `djf_surveys/validators.py` - Validation implementation
