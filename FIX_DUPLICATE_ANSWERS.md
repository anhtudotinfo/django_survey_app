# Fix: Duplicate Answers in CSV Export

## Problem

### Observed Issue:
When downloading survey responses as CSV, some columns showed duplicate data:
```
admin  2025-11-02 08:39:31  3  http://127.0.0.1:8000/download/file/80/
admin  2025-11-02 08:39:21  2  http://127.0.0.1:8000/download/file/78/
admin  2025-11-02 08:39:08  1  http://127.0.0.1:8000/download/file/76/
admin  2025-11-02 08:38:12  U  http://127.0.0.1:8000/download/file/74/
admin  2025-11-02 08:38:00  567  http://127.0.0.1:8000/download/file/72/
admin  2025-11-02 08:38:00  3   <-- DUPLICATE!
```

### Root Cause:
UserAnswer was being created **twice** for each survey submission:
1. Once in `CreateSurveyFormView` (for session tracking)
2. Again in `CreateSurveyForm.save()` (when saving form)

This resulted in:
- Multiple UserAnswer records for single submission
- Duplicate entries in database
- Duplicate data in CSV export
- Data inconsistency

## Solution Overview

### Key Changes:
1. Modified `CreateSurveyForm` to accept existing `user_answer` parameter
2. Moved UserAnswer creation logic entirely to view layer
3. Form now reuses UserAnswer from view instead of creating new one
4. Proper session-based tracking to prevent duplicates

## Implementation Details

### 1. Updated CreateSurveyForm (`djf_surveys/forms.py`)

**Before:**
```python
def __init__(self, survey, user, current_section=None, *args, **kwargs):
    self.survey = survey
    self.user = user
    super().__init__(...)

def save(self):
    # Always creates new UserAnswer - PROBLEM!
    user_answer = UserAnswer.objects.create(
        survey=self.survey, 
        user=self.user,
        direction=None
    )
    # Save answers to this UserAnswer...
```

**After:**
```python
def __init__(self, survey, user, current_section=None, user_answer=None, *args, **kwargs):
    self.survey = survey
    self.user = user
    self.user_answer = user_answer  # ✓ Accept existing UserAnswer
    super().__init__(...)

def save(self):
    # Use existing UserAnswer or create fallback
    if self.user_answer:
        user_answer = self.user_answer  # ✓ Reuse from view
    else:
        # Fallback only (shouldn't normally happen)
        user_answer = UserAnswer.objects.create(...)
    
    # Save answers to this UserAnswer...
```

### 2. Updated CreateSurveyFormView (`djf_surveys/views.py`)

**Added method:**
```python
def _get_or_create_user_answer(self):
    """Get or create UserAnswer for current survey session."""
    survey = self.get_object()
    
    if self.request.user.is_authenticated:
        # Check session first
        user_answer_id = self.request.session.get(f'survey_{survey.id}_user_answer_id')
        if user_answer_id:
            try:
                return UserAnswer.objects.get(id=user_answer_id, user=self.request.user)
            except UserAnswer.DoesNotExist:
                pass
        
        # Create new UserAnswer
        if survey.duplicate_entry:
            user_answer = UserAnswer.objects.create(...)
        else:
            user_answer, created = UserAnswer.objects.get_or_create(...)
        
        self.request.session[f'survey_{survey.id}_user_answer_id'] = user_answer.id
        return user_answer
    else:
        # Similar logic for anonymous users
        ...
```

**Updated get_form():**
```python
def get_form(self, form_class=None):
    form_class = form_class or self.get_form_class()
    current_section = self.get_current_section()
    survey = self.get_object()
    
    # ✓ Get UserAnswer from view
    user_answer = self._get_or_create_user_answer()
    
    return form_class(
        survey=survey,
        user=self.request.user,
        current_section=current_section,
        user_answer=user_answer,  # ✓ Pass to form
        **self.get_form_kwargs()
    )
```

## How It Works Now

### Flow:
```
1. User starts survey
   ↓
2. View: _get_or_create_user_answer()
   - Check session for user_answer_id
   - If found: retrieve existing
   - If not: create new & store in session
   ↓
3. View: get_form(user_answer=...)
   - Pass UserAnswer to form
   ↓
4. Form: save()
   - Use provided UserAnswer
   - Save all answers to it
   ↓
5. Result: Single UserAnswer with all answers
```

### Session Tracking:
```python
# Session key format:
'survey_{survey.id}_user_answer_id' = user_answer.id

# Example:
'survey_5_user_answer_id' = 123
```

## Benefits

### ✅ Fixes duplicate issue:
- Only ONE UserAnswer per submission
- No duplicate data in CSV
- Consistent database state

### ✅ Maintains functionality:
- Multi-section surveys work
- Draft save/resume works
- Duplicate entry surveys work
- Anonymous users work

### ✅ Better architecture:
- Clear separation of concerns
- View handles UserAnswer lifecycle
- Form handles Answer data only
- Session provides continuity

### ✅ Backward compatible:
- Existing surveys unaffected
- No data migration needed
- Fallback logic for edge cases

## Testing

### Test Case 1: Single Submission
```
1. User fills survey
2. Submits form
3. Check database:
   UserAnswer.objects.filter(survey=X, user=Y).count() == 1 ✓
4. Check CSV:
   Each submission appears once ✓
```

### Test Case 2: Multi-Section Survey
```
1. User starts survey
2. Completes section 1 (UserAnswer created, ID=100)
3. Navigates to section 2 (UserAnswer retrieved, ID=100)
4. Completes section 2 (Same UserAnswer ID=100)
5. Check database:
   All answers linked to UserAnswer ID=100 ✓
```

### Test Case 3: Duplicate Entry Survey
```
1. Survey has duplicate_entry=True
2. User submits first time (UserAnswer ID=100)
3. Session clears
4. User submits second time (UserAnswer ID=101)
5. Check database:
   2 separate UserAnswer records ✓
```

### Test Case 4: Anonymous User
```
1. Anonymous user starts survey
2. Session created
3. UserAnswer created (ID=100)
4. Session tracks ID=100
5. User completes survey
6. All answers linked to ID=100 ✓
```

## Files Modified

1. **djf_surveys/forms.py**
   - `CreateSurveyForm.__init__()`: Added `user_answer` parameter
   - `CreateSurveyForm.save()`: Use provided UserAnswer

2. **djf_surveys/views.py**
   - `CreateSurveyFormView._get_or_create_user_answer()`: New method
   - `CreateSurveyFormView.get_form()`: Pass UserAnswer to form

## Rollback Plan

If issues arise:
1. Revert `djf_surveys/forms.py` to create UserAnswer in save()
2. Revert `djf_surveys/views.py` to not pass user_answer
3. Note: This restores the duplicate issue

## Related Fixes

This fix complements the earlier MultipleObjectsReturned fix:
- **First fix:** Prevented error when multiple UserAnswers exist
- **This fix:** Prevents creating multiple UserAnswers in first place

Together, they ensure:
- No duplicate UserAnswers per submission
- No errors when multiple submissions exist
- Proper handling of duplicate_entry surveys

## Performance Impact

### Before:
- 2 INSERT queries per submission (2 UserAnswers)
- Extra database records
- Slower CSV generation

### After:
- 1 INSERT query per submission (1 UserAnswer)
- Cleaner database
- Faster CSV generation

**Performance:** Improved (~50% fewer UserAnswer records)

## Security Considerations

### Session Validation:
```python
# Always validate user ownership
user_answer = UserAnswer.objects.get(
    id=user_answer_id, 
    user=self.request.user  # ✓ Security check
)
```

### Scope:
- Session data: Survey-specific UserAnswer ID only
- Access: Limited to current user
- Lifetime: Session duration
- Risk: Low (user can only access their own data)

## Summary

### Problem:
- UserAnswer created twice per submission
- Duplicate data in database and CSV
- Data inconsistency

### Solution:
- Single UserAnswer creation point (view layer)
- Form reuses UserAnswer from view
- Session-based tracking for continuity

### Result:
- ✅ One UserAnswer per submission
- ✅ No duplicate data
- ✅ Better architecture
- ✅ Improved performance

---

**Fixed Date:** 2025-11-02  
**Status:** ✅ RESOLVED  
**Impact:** Critical bug fix  
**Breaking Changes:** None  
**Migration Required:** No
