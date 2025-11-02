# File Organization & Download Guide

## Overview
The survey system now supports flexible file organization with two modes: by response or by question. All files can be downloaded as a single ZIP archive with proper structure and metadata.

## Features

### 1. File Organization Modes

#### Mode 1: By Response (Default)
**Folder Structure:**
```
survey_{survey_id}/
├── response_{response_id_1}/
│   ├── Q{question_1_id}_{timestamp}_{filename}.pdf
│   ├── Q{question_2_id}_{timestamp}_{filename}.jpg
│   └── Q{question_3_id}_{timestamp}_{filename}.docx
├── response_{response_id_2}/
│   ├── Q{question_1_id}_{timestamp}_{filename}.pdf
│   └── Q{question_2_id}_{timestamp}_{filename}.jpg
└── ...
```

**Use Case:**
- When you want all files from one submission together
- Easy to see what one user uploaded
- Good for reviewing individual responses
- One folder = One complete submission

**File Naming Format:**
```
Q{question_id}_{timestamp}_{original_filename}

Example:
Q15_20250102_143025_resume.pdf
```

#### Mode 2: By Question
**Folder Structure:**
```
survey_{survey_id}/
├── question_{question_id_1}/
│   ├── R{response_1_id}_{timestamp}_{filename}.pdf
│   ├── R{response_2_id}_{timestamp}_{filename}.pdf
│   └── R{response_3_id}_{timestamp}_{filename}.pdf
├── question_{question_id_2}/
│   ├── R{response_1_id}_{timestamp}_{filename}.jpg
│   └── R{response_2_id}_{timestamp}_{filename}.jpg
└── ...
```

**Use Case:**
- When comparing answers to same question
- Bulk processing files for one question
- Analyzing patterns in file uploads
- One folder = All answers to one question

**File Naming Format:**
```
R{response_id}_{timestamp}_{original_filename}

Example:
R42_20250102_143025_document.pdf
```

### 2. File Naming Convention

#### Filename Components

1. **Prefix** (Q or R):
   - `Q{id}` = Question ID (in by-response mode)
   - `R{id}` = Response ID (in by-question mode)

2. **Timestamp**:
   - Format: `YYYYMMDD_HHMMSS`
   - Example: `20250102_143025`
   - Ensures uniqueness
   - Sortable chronologically

3. **Original Filename**:
   - Sanitized and validated
   - Maximum 50 characters
   - Special characters removed
   - Extension preserved

#### Full Examples

**By Response Mode:**
```
Q15_20250102_143025_resume.pdf
Q16_20250102_143030_photo.jpg
Q17_20250102_143035_transcript.pdf
```
Meaning:
- Files from same response in same folder
- Q15, Q16, Q17 = Question IDs
- Easy to identify which question each file answers

**By Question Mode:**
```
R42_20250102_143025_document.pdf
R43_20250102_150000_report.pdf
R44_20250102_160000_paper.pdf
```
Meaning:
- All answers to same question in same folder
- R42, R43, R44 = Response IDs
- Easy to compare different users' submissions

### 3. ZIP Download Feature

#### Contents of ZIP Archive

1. **All uploaded files** with proper folder structure
2. **README.txt** with:
   - Survey information
   - Organization type
   - File mapping (file → question → user)
   - Statistics
   
3. **file_list.csv** with:
   - File path
   - Question text
   - Response ID
   - Username
   - Upload date

#### README.txt Example
```
Survey Files Download
=====================

Survey Name: Customer Feedback Survey
Survey ID: 5
Organization Type: By Response (One folder per submission)
Download Date: 2025-01-02 14:30:25
Total Files: 12

File Organization:
- Files are organized by response/submission
- Each folder represents one user's submission
- Filename format: Q{question_id}_{timestamp}_{original_name}

File Mapping:
--------------------------------------------------------------------------------

File: survey_5/response_42/Q15_20250102_143025_resume.pdf
  Question: Please upload your resume
  Response ID: 42
  User: john_doe
  Uploaded: 2025-01-02 14:30

...

================================================================================
Statistics:
  Total files added to ZIP: 12
  Total size: 15.3 MB
```

#### file_list.csv Example
```csv
File Path,Question,Response ID,User,Upload Date
"survey_5/response_42/Q15_20250102_143025_resume.pdf","Please upload your resume",42,"john_doe","2025-01-02 14:30"
"survey_5/response_42/Q16_20250102_143030_photo.jpg","Upload your photo",42,"john_doe","2025-01-02 14:30"
...
```

## Usage

### Setting File Organization

#### In Admin Interface
1. Go to survey edit page
2. Find "File Organization" section
3. Choose one:
   - ⚪ By Response (One folder per submission)
   - ⚪ By Question (One folder per question)
4. Save survey

#### Via Code
```python
from djf_surveys.models import Survey

survey = Survey.objects.get(id=5)

# Set to organize by response
survey.file_organization = Survey.FILE_ORG_BY_RESPONSE
survey.save()

# Or organize by question
survey.file_organization = Survey.FILE_ORG_BY_QUESTION
survey.save()
```

### Downloading Survey Files

#### Via Admin Interface
1. Go to survey summary page
2. Click the **blue download button** (cloud icon)
3. ZIP file will be generated and downloaded
4. Filename format: `survey_{slug}_files_{timestamp}.zip`

#### Via URL
```
/download/survey-files/{survey-slug}/
```

**Requirements:**
- Must be logged in
- Must be staff/admin user
- Survey must have uploaded files

### Accessing File Statistics

```python
survey = Survey.objects.get(id=5)

stats = survey.get_file_statistics()
print(stats)
# Output: {
#     'file_count': 12,
#     'total_size_bytes': 16056320,
#     'total_size_mb': 15.31,
#     'organization_type': 'response',
#     'base_folder': 'survey_5',
# }
```

### Getting All Uploaded Files

```python
survey = Survey.objects.get(id=5)

files = survey.get_all_uploaded_files()
for answer in files:
    print(f"File: {answer.file_value.name}")
    print(f"  Question: {answer.question.label}")
    print(f"  User: {answer.user_answer.user.username}")
    print(f"  Size: {answer.file_value.size} bytes")
```

## Technical Details

### File Path Generation

The `upload_survey_file()` function automatically:

1. **Gets survey organization preference**
2. **Cleans filename** (removes special chars, limits length)
3. **Generates timestamp** for uniqueness
4. **Creates appropriate path** based on organization mode
5. **Returns full path** for Django FileField

### Database Schema

**Survey Model - New Field:**
```python
file_organization = models.CharField(
    max_length=20,
    choices=[
        ('response', 'By Response (One folder per submission)'),
        ('question', 'By Question (One folder per question)')
    ],
    default='response'
)
```

**No changes needed to Answer model** - existing `file_value` field is used.

### Security

- Only staff users can download ZIP archives
- Permission checks enforced
- File paths validated
- Secure file access through Django storage
- No direct filesystem access exposed

### Performance

- ZIP created in memory (no disk writes)
- Streaming response for large files
- Efficient file iteration
- Statistics cached in queryset

## Migration

Migration `0027_survey_file_organization` adds the new field:
```python
# All existing surveys default to 'response' mode
# No data migration needed
# Backward compatible
```

## Best Practices

### When to Use Each Mode

**Use "By Response" when:**
- ✅ You want to review each user's complete submission
- ✅ Files are related to same person/entity
- ✅ Downloading individual submissions
- ✅ Archiving complete responses

**Use "By Question" when:**
- ✅ Comparing answers to same question
- ✅ Bulk processing similar files
- ✅ Analyzing file patterns
- ✅ Quality checking specific questions

### File Naming Tips

1. **Original filenames** are preserved in the new name
2. **Timestamps** ensure no conflicts
3. **Prefixes** (Q/R) make identification easy
4. **Keep original filenames** descriptive for better tracking

### Download Tips

1. **Check file count** before downloading large surveys
2. **Use CSV file** in ZIP for spreadsheet analysis
3. **Read README.txt** first for orientation
4. **Archive old downloads** to save space
5. **Extract to dedicated folder** to avoid clutter

## Examples

### Example 1: Job Applications Survey

**Survey Setup:**
- Name: "Job Applications"
- Organization: By Response
- Questions: Resume, Cover Letter, Portfolio

**Result:**
```
survey_12/
├── response_101/
│   ├── Q5_20250102_100000_john_resume.pdf
│   ├── Q6_20250102_100015_john_cover.pdf
│   └── Q7_20250102_100030_john_portfolio.zip
├── response_102/
│   ├── Q5_20250102_110000_jane_resume.pdf
│   └── Q6_20250102_110015_jane_cover.pdf
└── ...
```

Each folder = One applicant's complete application

### Example 2: Photo Contest

**Survey Setup:**
- Name: "Photo Contest 2025"
- Organization: By Question
- Question: "Upload your photo"

**Result:**
```
survey_13/
└── question_8/
    ├── R201_20250102_090000_photo1.jpg
    ├── R202_20250102_091500_photo2.jpg
    ├── R203_20250102_093000_photo3.jpg
    └── ...
```

One folder = All contest entries for easy judging

## API Reference

### Survey Model Methods

```python
# Get upload folder path
survey.get_upload_folder_path()
# Returns: 'survey_{id}'

# Get all uploaded files
files = survey.get_all_uploaded_files()
# Returns: QuerySet of Answer objects with files

# Get file statistics
stats = survey.get_file_statistics()
# Returns: {
#     'file_count': int,
#     'total_size_bytes': int,
#     'total_size_mb': float,
#     'organization_type': str,
#     'base_folder': str
# }
```

### View Function

```python
@login_required
@staff_required
def download_survey_files(request, slug):
    """Download all files as ZIP"""
    # Returns: HttpResponse with ZIP file
    # Filename: survey_{slug}_files_{timestamp}.zip
```

## Troubleshooting

### Issue: Files Not in ZIP
**Cause**: Files deleted from filesystem but references remain in DB
**Solution**: Check file paths, verify media folder

### Issue: Large ZIP Takes Long Time
**Cause**: Many files or large total size
**Solution**: 
- Filter by date range (future feature)
- Download in smaller batches
- Optimize file sizes

### Issue: Wrong Folder Structure
**Cause**: Organization mode changed after files uploaded
**Solution**: Organization mode at upload time determines path

### Issue: Permission Denied
**Cause**: Not staff user
**Solution**: Contact admin for access

## Security Considerations

### File Access Control
- Only staff can download ZIP
- File paths validated
- No directory traversal
- Secure Django storage

### File Naming Security
- Special characters sanitized
- Path validation
- Length limits enforced
- No executable extensions allowed

### Privacy
- User information in README
- CSV contains usernames
- Only admins can access
- Respect survey privacy settings

## Future Enhancements

Potential improvements:
- [ ] Filter files by date range
- [ ] Download specific responses only
- [ ] Download specific questions only
- [ ] Batch download multiple surveys
- [ ] Cloud storage integration
- [ ] File preview before download
- [ ] Download statistics dashboard

## Support

For issues:
1. Check README.txt in ZIP
2. Review file_list.csv
3. Check Django logs
4. Contact system administrator

## Version History

- **v1.0** (2025-01-02): Initial implementation
  - Two organization modes
  - Intelligent file naming
  - ZIP download with metadata
  - Statistics tracking

---

**Status**: ✅ Production Ready
