# Survey Sections, Branch Logic, and File Upload - Implementation Summary

## ✅ Completed Features

### 1. **Multi-Section Surveys**
- ✓ Section model with ordering and description
- ✓ Questions can be assigned to sections
- ✓ Admin interface for managing sections
- ✓ Progress tracking across sections
- ✓ Backward compatible (surveys without sections work as before)

### 2. **Branch Logic / Conditional Navigation**
- ✓ BranchRule model with operators: equals, not_equals, contains, in
- ✓ Priority-based rule evaluation
- ✓ Automatic navigation based on user answers
- ✓ Validation to prevent circular references
- ✓ Warnings for unreachable sections
- ✓ Admin interface with inline branch rules

### 3. **Draft Response System**
- ✓ Save survey progress at any time
- ✓ Auto-save when navigating between sections
- ✓ Resume from last section
- ✓ Works for both authenticated and anonymous users
- ✓ Automatic expiration after 30 days (configurable)
- ✓ Draft cleanup management command

### 4. **File Upload Field Type**
- ✓ New file upload question type
- ✓ File type validation (images, PDF, Office docs)
- ✓ File size validation (10MB default, configurable)
- ✓ Protected file download with access control
- ✓ Filename sanitization
- ✓ MIME type verification

## 📁 New Files Created

### Models & Logic
- `djf_surveys/branch_logic.py` - BranchEvaluator class
- `djf_surveys/navigation.py` - SectionNavigator for multi-section navigation
- `djf_surveys/draft_service.py` - DraftService for save/load/cleanup

### Management Commands
- `djf_surveys/management/commands/cleanup_expired_drafts.py`
- `djf_surveys/management/commands/cleanup_orphaned_files.py`

### Templates
- `djf_surveys/templates/djf_surveys/components/section_progress.html`
- `djf_surveys/templates/djf_surveys/components/section_navigation.html`
- `djf_surveys/templates/djf_surveys/components/draft_resume_banner.html`

## 🔧 Modified Files

### Core Models
- `djf_surveys/models.py`:
  - Added `Section` model
  - Added `DraftResponse` model
  - Added `BranchRule` model with validation
  - Added `file` to TYPE_FIELD (value=10)
  - Added `file_value` to Answer model
  - Added `section` FK to Question model
  - Added validation methods and circular reference detection

### Forms
- `djf_surveys/forms.py`:
  - Updated BaseSurveyForm to accept `current_section` parameter
  - Added file upload field handling
  - Filter questions by section
  - Updated CreateSurveyForm to save file uploads

### Views
- `djf_surveys/views.py`:
  - Updated CreateSurveyFormView with section navigation
  - Integrated DraftService for save/load/resume
  - Added action handlers: save_draft, next, previous, submit
  - Branch logic evaluation on navigation
  - Added `download_survey_file` view for protected downloads

### Admin
- `djf_surveys/admin.py`:
  - Added SectionAdmin with BranchRuleInline
  - Added DraftResponseAdmin
  - Updated SurveyAdmin with SectionInline
  - Updated QuestionAdmin with section filter
  - Added circular reference warnings

### Validators
- `djf_surveys/validators.py`:
  - Added FileTypeValidator
  - Added FileSizeValidator

### Settings
- `moi/settings.py`:
  - Added SURVEY_FILE_UPLOAD_MAX_SIZE
  - Added SURVEY_FILE_ALLOWED_TYPES
  - Added SURVEY_DRAFT_EXPIRY_DAYS

### URLs
- `djf_surveys/urls.py`:
  - Added download_file URL pattern

### Templates
- `djf_surveys/templates/djf_surveys/form.html`:
  - Added progress bar component
  - Added draft resume banner
  - Added section navigation buttons
  - Added `enctype="multipart/form-data"` for file uploads

## 🗄️ Database Changes

### New Tables
- `djf_surveys_section` - Survey sections
- `djf_surveys_draftresponse` - Draft responses
- `djf_surveys_branchrule` - Branch navigation rules

### Modified Tables
- `djf_surveys_question` - Added `section_id` (nullable FK)
- `djf_surveys_answer` - Added `file_value` (FileField)

### Migration Files
- `0023_answer_file_value_alter_question_type_field_section_and_more.py`
- `0024_create_default_sections.py` (data migration)

## 🎯 Key Features Breakdown

### Section Management
```python
# Create sections in admin
Section.objects.create(
    survey=survey,
    name="Personal Information",
    description="Tell us about yourself",
    ordering=1
)
```

### Branch Logic
```python
# Create branch rule in admin
BranchRule.objects.create(
    section=section1,
    condition_question=question_age,
    condition_operator='equals',
    condition_value='18',
    next_section=section3,  # Skip section2
    priority=0
)
```

### Draft System
```python
# Save draft
DraftService.save_draft(
    survey=survey,
    data={question_id: answer_value},
    user=user,
    current_section=section
)

# Load draft
draft = DraftService.load_draft(survey=survey, user=user)
```

### File Upload
```python
# Question with file upload
Question.objects.create(
    survey=survey,
    section=section,
    type_field=TYPE_FIELD.file,
    label="Upload your CV"
)
```

## 🔒 Security Features

1. **File Upload Security**
   - File type whitelist validation
   - MIME type verification
   - File size limits
   - Filename sanitization (prevents path traversal)
   - Private storage (not in public MEDIA_URL)

2. **File Download Access Control**
   - Login required
   - Permission check: admin, owner, or public survey
   - Protected view serving files

3. **Draft Access Control**
   - User/session isolation
   - No cross-user draft access

## 📝 Configuration

Add to `settings.py`:
```python
# File Upload Settings
SURVEY_FILE_UPLOAD_MAX_SIZE = 10 * 1024 * 1024  # 10MB
SURVEY_FILE_ALLOWED_TYPES = ['jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx', 'xls', 'xlsx']
SURVEY_DRAFT_EXPIRY_DAYS = 30
```

## 🔄 Scheduled Tasks (Cron Jobs)

Add to crontab:
```bash
# Cleanup expired drafts daily at 2 AM
0 2 * * * cd /path/to/project && python manage.py cleanup_expired_drafts

# Cleanup orphaned files weekly on Sunday at 3 AM
0 3 * * 0 cd /path/to/project && python manage.py cleanup_orphaned_files
```

## 🎨 UI Components

### Progress Bar
Shows current section and percentage complete

### Navigation Buttons
- **Previous**: Go to previous section (sequential)
- **Save Draft**: Save progress without validation
- **Next**: Validate and go to next section (may trigger branch logic)
- **Submit**: Final submission (shown on last section)

### Draft Resume Banner
Displayed when user has saved draft, prompts to continue

## 🧪 Testing

Run system check:
```bash
python manage.py check
```

Test migrations:
```bash
python manage.py migrate --plan
python manage.py migrate
```

Test cleanup commands:
```bash
python manage.py cleanup_expired_drafts
python manage.py cleanup_orphaned_files --dry-run
```

## 📊 Backward Compatibility

All existing surveys continue to work without modification:
- Questions without sections → assigned to default "Main" section
- Surveys without sections → behave as single-page forms
- No branch rules → sequential navigation
- Existing field types unchanged

## 🚀 Usage Flow

### Admin Setup
1. Create survey
2. Add sections with ordering
3. Assign questions to sections
4. (Optional) Create branch rules for conditional navigation
5. (Optional) Add file upload questions

### User Experience
1. User starts survey → shown first section
2. Fills out questions in current section
3. Can save draft at any time
4. Clicks Next → validates, saves draft, navigates (with branch logic)
5. Can click Previous to go back
6. On last section, clicks Submit → final submission
7. Draft automatically deleted on submission

### Resume Flow
1. User returns to incomplete survey
2. Sees "saved draft" banner
3. Automatically taken to last active section
4. Previous answers are pre-filled
5. Can continue from where they left off

## 📈 Performance Considerations

- Branch rules evaluated efficiently with priority sorting
- Section queries optimized with `select_related`
- Draft data stored as JSON (not individual answer records)
- File uploads use chunked reading for large files
- Indexes added on frequently queried fields

## ✨ Best Practices

1. **Section Design**: Group related questions, keep sections focused
2. **Branch Logic**: Keep rules simple, test thoroughly, avoid deep nesting
3. **File Uploads**: Set appropriate size limits, specify accepted types
4. **Drafts**: Regular cleanup prevents database bloat
5. **Testing**: Test with multiple sections and branch scenarios

## 🎉 Implementation Complete!

All planned features have been successfully implemented and tested.
