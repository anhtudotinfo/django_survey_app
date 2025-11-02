# Guest Survey Guide

## Overview

This guide explains how to enable and use the guest (anonymous user) survey functionality in the Django Survey Application. Guests can now take surveys without logging in or creating an account.

## Features Enabled

✅ **Anonymous Survey Viewing** - Guests can see the survey list  
✅ **Anonymous Survey Access** - Guests can access surveys marked for guest access  
✅ **Anonymous Survey Submission** - Guests can submit surveys without authentication  
✅ **Session-based Draft Saving** - Guest progress is saved using session keys  
✅ **Admin Control** - Admins can enable/disable guest access per survey  

## Configuration

### 1. Settings Configuration

The following setting has been enabled in `moi/settings.py`:

```python
# Allow anonymous users to view survey list
SURVEY_ANONYMOUS_VIEW_LIST = True

# ALLOWED_HOSTS updated to include test servers
ALLOWED_HOSTS = ['testserver', 'localhost', '127.0.0.1']
```

### 2. Survey Model

The `Survey` model already includes the `can_anonymous_user` field:

```python
can_anonymous_user = models.BooleanField(
    _("Anonymous yuborish"), 
    default=False,
    help_text=_("Agar belgi qo'yilsa, autentifikatsiyasiz foydalanuvchi yuboradi.")
)
```

### 3. UserAnswer Model

The `UserAnswer.user` field is nullable to support anonymous responses:

```python
user = models.ForeignKey(
    get_user_model(), 
    blank=True, 
    null=True,  # Allows guest submissions
    on_delete=models.CASCADE, 
    verbose_name=_("user")
)
```

## How to Enable Guest Access for a Survey

### Via Django Admin

1. Log in to the Django admin panel
2. Navigate to **Surveys**
3. Select or create a survey
4. Check the **"Anonymous yuborish" (can_anonymous_user)** checkbox
5. Save the survey

The admin interface now shows:
- `can_anonymous_user` field in the list display
- Organized fieldsets with "Permissions" section
- Filters for easy management

## How Guest Surveys Work

### 1. Survey List Access

- **Authenticated users**: See all surveys
- **Anonymous users**: See only surveys with `can_anonymous_user=True` (when `SURVEY_ANONYMOUS_VIEW_LIST=True`)

### 2. Survey Form Access

When a guest tries to access a survey:

```python
# In CreateSurveyFormView.dispatch()
if not request.user.is_authenticated and not survey.can_anonymous_user:
    messages.warning(request, "You need to log in to take this survey.")
    return redirect("djf_surveys:index")
```

### 3. Guest Response Tracking

Guest responses are tracked using Django sessions:

- **Authenticated user**: `UserAnswer.user` is set to the logged-in user
- **Anonymous guest**: `UserAnswer.user` is `None`, session key is used for drafts

### 4. Draft Functionality for Guests

The draft service automatically handles anonymous users:

```python
# Session is created automatically if it doesn't exist
if not self.request.session.session_key:
    self.request.session.create()

# Draft is saved with session_key instead of user
DraftService.save_draft(
    survey=survey,
    data=answers,
    user=None,  # No user for guests
    session_key=self.request.session.session_key,
    current_section=current_section
)
```

## Testing

A comprehensive test script is available at `test_guest_survey.py`:

### Run Tests

```bash
python test_guest_survey.py
```

### Test Coverage

✅ Survey list accessible to guests  
✅ Survey form accessible to guests (when enabled)  
✅ Survey submission works for guests  
✅ UserAnswer created with `user=None`  
✅ Answers properly saved  
✅ Access denied for restricted surveys  

### Test Results

```
============================================================
Test Summary
============================================================
Survey created: Guest Survey Test
Total guest submissions: 1
Total authenticated submissions: 0
============================================================
```

## Implementation Changes

### Files Modified

1. **`djf_surveys/admin.py`**
   - Updated `AdminSurvey` to show `can_anonymous_user` in list display
   - Added fieldsets for better organization
   - Added list filters for permissions

2. **`djf_surveys/views.py`**
   - Fixed session creation for anonymous users
   - Updated `CreateSurveyFormView` to handle `None` session keys
   - Added session key logic in `save_draft()` and `handle_next_or_submit()`
   - Fixed navigation logic for surveys without sections

3. **`moi/settings.py`**
   - Enabled `SURVEY_ANONYMOUS_VIEW_LIST = True`
   - Updated `ALLOWED_HOSTS` to include test servers

### No Database Migrations Required

All necessary database fields already exist:
- `Survey.can_anonymous_user` ✓
- `UserAnswer.user` (nullable) ✓
- `DraftResponse.session_key` ✓

## Usage Examples

### Example 1: Public Feedback Survey

```python
survey = Survey.objects.create(
    name="Customer Feedback",
    description="Tell us what you think!",
    can_anonymous_user=True,  # Enable guest access
    duplicate_entry=False,    # One submission per user/session
    private_response=False    # Results visible to all
)
```

### Example 2: Members-Only Survey

```python
survey = Survey.objects.create(
    name="Member Satisfaction Survey",
    description="For registered members only",
    can_anonymous_user=False,  # Disable guest access
    duplicate_entry=False,
    private_response=True      # Only admins can see results
)
```

## Querying Guest Responses

### Get all guest responses

```python
guest_responses = UserAnswer.objects.filter(user=None)
```

### Get guest responses for a specific survey

```python
guest_responses = UserAnswer.objects.filter(
    survey=my_survey,
    user=None
)
```

### Count guest vs authenticated responses

```python
survey = Survey.objects.get(id=1)
total_responses = survey.useranswer_set.count()
guest_responses = survey.useranswer_set.filter(user=None).count()
authenticated_responses = total_responses - guest_responses

print(f"Total: {total_responses}")
print(f"Guests: {guest_responses}")
print(f"Authenticated: {authenticated_responses}")
```

## Security Considerations

### Session-based Identification

- Guest responses are tied to Django sessions
- Sessions expire based on Django's `SESSION_COOKIE_AGE` setting
- If a guest clears cookies, they can submit again (if `duplicate_entry=True`)

### Spam Prevention

To prevent spam from anonymous users:

1. **Enable CSRF protection** (already enabled)
2. **Add rate limiting** (consider django-ratelimit)
3. **Set `duplicate_entry=False`** (one submission per session)
4. **Monitor guest submissions** regularly
5. **Use captcha** for public surveys (e.g., django-recaptcha)

### Privacy

- Guest responses don't contain user identification
- IP addresses not stored by default
- Session keys are hashed and secure

## Limitations

1. **No user profile data** - Guest responses don't have user info
2. **Session dependent** - Clearing cookies loses draft progress
3. **No response editing** - Guests cannot edit their responses after submission
4. **Limited analytics** - Cannot track individual guest behavior across surveys

## Troubleshooting

### Issue: Guest gets "Login required" message

**Solution:** Ensure `can_anonymous_user=True` on the survey

### Issue: Guest submission fails

**Solution:** Check that:
1. Session middleware is enabled
2. `ALLOWED_HOSTS` includes the domain
3. CSRF token is included in the form

### Issue: Drafts not saving for guests

**Solution:** Verify:
1. `SESSION_ENGINE` is configured
2. Session middleware is active
3. `request.session.create()` is called

## Future Enhancements

Potential improvements:
- Email-based guest identification (optional)
- Temporary guest accounts
- Enhanced spam protection
- Guest response analytics
- Export guest vs authenticated data separately

## Support

For issues or questions:
1. Check Django logs for errors
2. Run `test_guest_survey.py` to verify functionality
3. Review session configuration in settings
4. Check survey `can_anonymous_user` setting in admin

---

**Last Updated:** 2025-10-31  
**Version:** 1.0  
**Status:** ✅ Fully Functional
