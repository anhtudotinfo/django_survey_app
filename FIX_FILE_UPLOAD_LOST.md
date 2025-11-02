# Fix: File Upload Lost After Submission

## Problem
Files uploaded in surveys were not saved. After submission, `file_value` field was empty.

## Root Cause
In `_save_current_section_answers()` (multi-section surveys), only the `value` field was saved:

```python
# WRONG - Only saves 'value', not 'file_value'
Answer.objects.update_or_create(
    question=question,
    user_answer=user_answer,
    defaults={'value': value}  # ❌ File lost!
)
```

For file uploads, the actual file is stored in `file_value` field, not `value` field!

## Solution

### Fix 1: Handle File Uploads in `_save_current_section_answers()`

**File:** `djf_surveys/views.py` (Line 508-526)

```python
# Prepare defaults based on question type
if question.type_field == TYPE_FIELD.file:
    # For file uploads, save to file_value field
    defaults = {
        'value': '',  # Empty string for file fields
        'file_value': value  # ✓ Save file here!
    }
elif isinstance(value, list):
    # For multi-select, join values
    defaults = {'value': ",".join(value)}
else:
    # For other types, save directly
    defaults = {'value': value}

# Update or create answer
Answer.objects.update_or_create(
    question=question,
    user_answer=user_answer,
    defaults=defaults  # ✓ Correct defaults
)
```

### Fix 2: Don't Delete Answers for Multi-Section Surveys

**File:** `djf_surveys/forms.py` (Line 232-248)

```python
if self.user_answer:
    user_answer = self.user_answer
    # For multi-section surveys, don't delete answers
    should_delete_answers = False
else:
    # Fallback for non-section surveys
    user_answer = UserAnswer.objects.create(...)
    should_delete_answers = True

# Only delete for non-section surveys
if should_delete_answers:
    Answer.objects.filter(user_answer=user_answer).delete()
```

## How It Works Now

### Multi-Section Survey Flow:

```
Section 1: User uploads file
  ↓
_save_current_section_answers()
  ↓
update_or_create with file_value field
  ↓
File saved to: file_value ✓
  ↓
Section 2: User fills other questions
  ↓
_save_current_section_answers()
  ↓
update_or_create (doesn't touch Section 1 answers)
  ↓
Final submit
  ↓
form.save() SKIPPED (answers already saved)
  ↓
✓ File preserved!
```

### Single Survey Flow:

```
User fills form with file
  ↓
form.save()
  ↓
Creates Answer with file_value
  ↓
✓ File saved!
```

## Database Schema

### Answer Model:
```python
class Answer(BaseModel):
    question = ForeignKey(Question)
    value = TextField()           # ← Text answers
    file_value = FileField()      # ← File uploads
    user_answer = ForeignKey(UserAnswer)
```

### Correct Usage:
- **Text/Radio/Select:** Save to `value` field
- **File Upload:** Save to `file_value` field, `value` = ''
- **Multi-select:** Save to `value` field (comma-separated)

## Testing

### Test File Upload:
```python
# Create test survey with file question
question = Question.objects.create(
    survey=survey,
    label='Upload Document',
    type_field=TYPE_FIELD.file
)

# Submit survey with file
# ... form submission ...

# Verify file saved
answer = Answer.objects.get(question=question, user_answer=ua)
assert answer.file_value, "File should be saved"
assert answer.file_value.name, "File should have filename"

# Verify file exists on disk
import os
from django.conf import settings
path = os.path.join(settings.MEDIA_ROOT, answer.file_value.name)
assert os.path.exists(path), "File should exist on disk"
```

### Manual Test:
1. Create survey with file upload question
2. Upload a file and submit
3. Check database:
   ```python
   answer = Answer.objects.latest('id')
   print(f"file_value: {answer.file_value}")  # Should show path
   print(f"value: {answer.value}")  # Should be empty
   ```
4. Verify file exists in media folder

## Common Mistakes to Avoid

### ❌ Wrong:
```python
# Saving file to 'value' field
defaults = {'value': file_upload}
```

### ❌ Wrong:
```python
# Not differentiating file fields
defaults = {'value': cleaned_data[field_name]}
```

### ✅ Correct:
```python
if question.type_field == TYPE_FIELD.file:
    defaults = {
        'value': '',
        'file_value': cleaned_data[field_name]
    }
else:
    defaults = {'value': cleaned_data[field_name]}
```

## Files Modified

1. **djf_surveys/views.py**
   - Line 508-526: Enhanced `_save_current_section_answers()`
   - Added file type detection
   - Proper `file_value` handling

2. **djf_surveys/forms.py**
   - Line 232-248: Conditional answer deletion
   - Preserve answers for multi-section surveys

## Impact

### Before Fix:
- ❌ Files uploaded but not saved
- ❌ `file_value` field empty
- ❌ CSV export shows "No file"
- ❌ Users lose uploaded files

### After Fix:
- ✅ Files saved correctly
- ✅ `file_value` field populated
- ✅ CSV export shows file URL and path
- ✅ Files preserved on disk

## Related Files

File organization uses survey's `file_organization` setting:
- **By Response:** `/media/survey_uploads/{survey_id}/{response_id}/{filename}`
- **By Question:** `/media/survey_uploads/{survey_id}/{question_id}/{filename}`

## Status

✅ **FIXED**
- File uploads work correctly
- Multi-section surveys preserve files
- Single surveys preserve files
- CSV export includes file paths

**Date:** 2025-11-02
