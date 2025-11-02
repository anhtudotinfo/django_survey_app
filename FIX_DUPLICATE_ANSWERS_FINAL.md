# Fix: Duplicate Answers Error

## Error
```
MultipleObjectsReturned at /create/test/
get() returned more than one Answer -- it returned 2!
```

## Root Cause
When form is submitted multiple times (e.g., validation errors, resubmission), `Answer` objects were created each time without deleting old ones, causing duplicates.

## Solution
Delete existing answers before creating new ones in `CreateSurveyForm.save()`:

```python
# Delete existing answers to prevent duplicates
Answer.objects.filter(user_answer=user_answer).delete()

# Then create new answers
for question in self.questions:
    Answer.objects.create(...)
```

## Impact
- ✅ Prevents duplicate Answer objects
- ✅ Form can be resubmitted without errors
- ✅ Clean data in database
- ⚠️ Old answers are replaced (intended behavior)

## File Modified
- `djf_surveys/forms.py` - Line 242-244 added

**Status:** ✅ FIXED
