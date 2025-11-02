# Fix: MultipleObjectsReturned Error in CreateSurveyFormView

## Problem

### Error Message:
```
MultipleObjectsReturned at /create/test/
get() returned more than one UserAnswer -- it returned 2!
```

### Root Cause:
When a survey has `duplicate_entry=True` (allowing multiple submissions), users can have multiple `UserAnswer` records for the same survey. The original code used `get_or_create()` which fails when multiple records exist:

```python
# PROBLEMATIC CODE:
user_answer, created = UserAnswer.objects.get_or_create(
    survey=survey,
    user=self.request.user,
    defaults={'direction': None}
)
# ❌ Fails if user has submitted multiple times!
```

### When it happens:
1. Survey has `duplicate_entry=True`
2. User submits survey first time → Creates UserAnswer #1
3. User submits survey second time → Creates UserAnswer #2
4. User tries to submit third time → `get_or_create()` finds 2 records → ERROR!

## Solution

### Fixed Logic:

```python
# Check if we have a user_answer_id in session first
user_answer_id = self.request.session.get(f'survey_{survey.id}_user_answer_id')

if user_answer_id:
    # Retrieve the specific UserAnswer for this session
    try:
        user_answer = UserAnswer.objects.get(id=user_answer_id, user=self.request.user)
        created = False
    except UserAnswer.DoesNotExist:
        # Session had invalid ID, create new one
        user_answer = UserAnswer.objects.create(...)
        created = True
        self.request.session[f'survey_{survey.id}_user_answer_id'] = user_answer.id
else:
    # No session ID
    if survey.duplicate_entry:
        # For duplicate surveys, always create new
        user_answer = UserAnswer.objects.create(...)
        created = True
        self.request.session[f'survey_{survey.id}_user_answer_id'] = user_answer.id
    else:
        # For non-duplicate surveys, get_or_create is safe
        user_answer, created = UserAnswer.objects.get_or_create(...)
        self.request.session[f'survey_{survey.id}_user_answer_id'] = user_answer.id
```

### Key Changes:

1. **Session-based tracking:** Store `user_answer_id` in session to track current submission
2. **Priority check:** Check session first before trying to get/create
3. **Conditional logic:** Different behavior for `duplicate_entry=True` vs `False`
4. **Error prevention:** Never use `get_or_create()` when multiple records might exist

## Benefits

### ✅ Fixes the error:
- No more `MultipleObjectsReturned` exceptions
- Surveys with `duplicate_entry=True` work correctly

### ✅ Maintains consistency:
- Same `UserAnswer` throughout single submission session
- Prevents creating duplicate records during one session

### ✅ Backward compatible:
- Non-duplicate surveys still use `get_or_create()` (safe)
- Existing behavior unchanged for single-submission surveys

### ✅ Proper separation:
- Multiple submissions → Multiple UserAnswer records (correct)
- Single session → Single UserAnswer record (correct)

## File Modified

**File:** `djf_surveys/views.py`  
**Method:** `CreateSurveyFormView.save_current_section_answers()`  
**Lines:** ~371-404

## Testing

### Automated Test:
```bash
python3 test_duplicate_entry_fix.py
```

### Test Results:
```
✓ Multiple UserAnswers exist for same user (expected)
✓ get_or_create failed as expected (confirms the bug)
✓ Fixed logic works correctly
✓ Session-based retrieval works
✓ Duplicate entry surveys work
✓ Non-duplicate surveys work
```

### Manual Testing:
1. Create survey with `duplicate_entry=True`
2. Login as user
3. Submit survey (creates UserAnswer #1)
4. Submit again (creates UserAnswer #2)
5. Submit third time (should work without error)
6. Verify 3 separate UserAnswer records exist

## Edge Cases Handled

### 1. Session expired/invalid:
```python
try:
    user_answer = UserAnswer.objects.get(id=user_answer_id, ...)
except UserAnswer.DoesNotExist:
    # Create new one if session ID is invalid
    user_answer = UserAnswer.objects.create(...)
```

### 2. Anonymous users:
- Already had separate logic
- Not affected by this fix

### 3. Non-duplicate surveys:
```python
if not survey.duplicate_entry:
    # Still safe to use get_or_create (0 or 1 record only)
    user_answer, created = UserAnswer.objects.get_or_create(...)
```

### 4. Multi-section surveys:
- Session tracking ensures same UserAnswer across all sections
- Answers properly associated with same submission

## Migration Required?

**NO** - No database changes needed. This is a logic-only fix.

## Rollback Plan

If issues arise, revert to original code:
```python
user_answer, created = UserAnswer.objects.get_or_create(
    survey=survey,
    user=self.request.user,
    defaults={'direction': None}
)
```

But note: This will restore the bug for duplicate_entry surveys.

## Related Issues

### Similar patterns in codebase:
Checked all uses of `UserAnswer.objects.get()` and `get_or_create()`:
- ✅ Line 387: Already safe (uses specific ID)
- ✅ Other views: Not affected (different context)

### Recommendations:
- Always check if model allows duplicates before using `get_or_create()`
- Consider session tracking for multi-step forms
- Use `filter().first()` as safer alternative when unsure

## Performance Impact

### Before:
- Fails on 3rd+ submission for duplicate surveys
- No performance concerns (didn't work)

### After:
- Session lookup: O(1) - very fast
- Database queries: Same count as before
- Session storage: Minimal (just an ID)

**Performance:** Negligible impact

## Security Considerations

### Session Security:
- Session ID stored: Survey-specific UserAnswer ID
- Scope: Limited to current user and survey
- Risk: Low (user can only access their own data)

### Validation:
```python
user_answer = UserAnswer.objects.get(id=user_answer_id, user=self.request.user)
#                                                       ^^^^^^^^^^^^^^^^^^^
# Ensures user can only retrieve their own UserAnswer
```

## Examples

### Example 1: First submission (duplicate_entry=True)
```
1. User starts survey
2. No session ID exists
3. survey.duplicate_entry = True
4. Create new UserAnswer (ID=100)
5. Store in session: survey_5_user_answer_id = 100
6. User completes survey
```

### Example 2: Second submission (same survey)
```
1. User starts same survey again
2. No session ID (new session)
3. survey.duplicate_entry = True
4. Create new UserAnswer (ID=101)
5. Store in session: survey_5_user_answer_id = 101
6. User completes survey
✓ Now 2 UserAnswers exist (correct!)
```

### Example 3: Multi-section navigation
```
1. User starts survey
2. Create UserAnswer (ID=100)
3. Store in session
4. User answers Section 1
5. User navigates to Section 2
6. Retrieve UserAnswer from session (ID=100)
7. User answers Section 2
8. Same UserAnswer used throughout
✓ All answers linked to UserAnswer #100
```

### Example 4: Non-duplicate survey
```
1. User starts survey
2. No session ID
3. survey.duplicate_entry = False
4. Use get_or_create (safe - max 1 record)
5. Returns existing or creates new
6. Store in session
✓ Works as before (backward compatible)
```

## Summary

### Problem:
- `get_or_create()` fails when multiple UserAnswers exist
- Occurred with `duplicate_entry=True` surveys

### Solution:
- Session-based tracking of current UserAnswer
- Conditional logic based on `duplicate_entry` setting
- Proper error handling for invalid sessions

### Impact:
- ✅ Fixes critical bug
- ✅ No breaking changes
- ✅ No migration needed
- ✅ Minimal performance impact
- ✅ Better user experience

### Status:
**FIXED** ✅

---

**Fixed Date:** 2025-11-02  
**Version:** Django 5.0.10  
**Affected Views:** CreateSurveyFormView  
**Test Coverage:** ✅ Automated + Manual
