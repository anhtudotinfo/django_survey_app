# Survey Draft System Guide

## Overview

The Draft Response system allows users to save their survey progress and resume later. This is especially useful for:

- **Long surveys**: Multi-section surveys that take time to complete
- **Interrupted sessions**: Users can leave and return without losing data
- **Mobile users**: Save on one device, continue on another (if authenticated)
- **Data quality**: Users can take breaks and return with fresher focus

## Key Features

- **Auto-save**: Progress automatically saved when navigating between sections
- **Manual save**: Users can explicitly save draft at any time
- **Resume prompt**: Returning users see option to resume where they left off
- **Expiration**: Drafts auto-expire after configurable period (default 30 days)
- **Anonymous support**: Works for both authenticated and anonymous users
- **Section tracking**: Remembers which section user was on

## How It Works

### For Authenticated Users

1. User starts survey (logged in)
2. User answers questions in Section 1
3. User clicks "Next" or "Save Draft"
4. **Draft saved** with user ID
5. User leaves site
6. User returns later (same or different device)
7. **Resume banner shown**: "You have a draft in progress"
8. User clicks "Resume"
9. Returns to saved section with previous answers filled in
10. User completes survey
11. **Draft deleted** on final submission

### For Anonymous Users

1. User starts survey (not logged in)
2. Django session created
3. User answers questions
4. **Draft saved** with session key
5. User leaves site (keeps browser open)
6. User returns (same browser session)
7. **Resume banner shown**
8. User resumes from saved point
9. User completes survey
10. **Draft deleted** on final submission

**Note**: Anonymous drafts only work within same browser session. Closing browser may clear session.

## Configuration

### Settings (moi/settings.py)

```python
# Draft expiration in days (default: 30)
SURVEY_DRAFT_EXPIRY_DAYS = 30

# Session configuration for anonymous users
SESSION_COOKIE_AGE = 1209600  # 2 weeks in seconds
SESSION_SAVE_EVERY_REQUEST = True
```

### Customization

```python
# Shorter expiration for temporary surveys
SURVEY_DRAFT_EXPIRY_DAYS = 7  # 1 week

# Longer expiration for complex surveys
SURVEY_DRAFT_EXPIRY_DAYS = 90  # 3 months

# Extend session lifetime for anonymous users
SESSION_COOKIE_AGE = 2592000  # 30 days
```

## Data Storage

### DraftResponse Model

Located in `djf_surveys/models.py`:

```python
class DraftResponse(BaseModel):
    survey = ForeignKey(Survey)           # Which survey
    user = ForeignKey(User, null=True)    # Authenticated user (optional)
    session_key = CharField(null=True)    # Anonymous session (optional)
    current_section = ForeignKey(Section) # Where user left off
    data = JSONField()                     # Question answers as JSON
    expires_at = DateTimeField()          # When draft expires
```

### Data Structure

The `data` field stores answers as JSON:

```json
{
  "15": "John Doe",           // question_id: answer
  "16": "john@example.com",
  "17": "Yes",
  "18": ["Option 1", "Option 2"]
}
```

**Important**: 
- Keys are question IDs (integers)
- Values are answer values (strings, numbers, arrays)
- **Files are NOT stored** in drafts (only saved on final submission)

## User Interface

### Save Draft Button

Appears on survey form:

```html
<button type="submit" name="action" value="save_draft">
    💾 Save Draft
</button>
```

### Resume Banner

Shown when draft exists:

```html
<div class="draft-resume-banner">
    ⚠️ You have a draft in progress from [date].
    <a href="?resume_draft=1">Resume</a> or 
    <a href="?discard_draft=1">Start Over</a>
</div>
```

### Progress Indicator

Shows current section and total:

```html
<div class="section-progress">
    Section 2 of 4
    <div class="progress-bar">
        <div class="progress-fill" style="width: 50%"></div>
    </div>
</div>
```

## DraftService API

Located in `djf_surveys/draft_service.py`, provides methods for draft management.

### Save Draft

```python
from djf_surveys.draft_service import DraftService

# For authenticated user
draft = DraftService.save_draft(
    survey=survey,
    data={15: "answer1", 16: "answer2"},
    user=request.user,
    current_section=section
)

# For anonymous user
draft = DraftService.save_draft(
    survey=survey,
    data={15: "answer1", 16: "answer2"},
    session_key=request.session.session_key,
    current_section=section
)
```

**Parameters**:
- `survey`: Survey object
- `data`: Dict of question_id → answer_value
- `user`: User object (optional, for authenticated)
- `session_key`: Session key (optional, for anonymous)
- `current_section`: Section object (where user is)

**Returns**: DraftResponse object (created or updated)

**Behavior**:
- If draft exists: Updates with new data (merges)
- If no draft: Creates new draft
- Refreshes expiration date on each save

### Load Draft

```python
# For authenticated user
draft = DraftService.load_draft(
    survey=survey,
    user=request.user
)

# For anonymous user
draft = DraftService.load_draft(
    survey=survey,
    session_key=request.session.session_key
)
```

**Returns**: 
- DraftResponse object if found and not expired
- None if no draft or expired

### Delete Draft

```python
# For authenticated user
deleted = DraftService.delete_draft(
    survey=survey,
    user=request.user
)

# For anonymous user
deleted = DraftService.delete_draft(
    survey=survey,
    session_key=request.session.session_key
)
```

**Returns**: True if deleted, False if not found

### Convert to Final Response

```python
# After final submission
DraftService.convert_to_final(draft)
```

Called automatically by form submission. Deletes draft after final response saved.

### Cleanup Expired Drafts

```python
# Run periodically (cron job)
deleted_count = DraftService.cleanup_expired_drafts()
```

**Returns**: Number of expired drafts deleted

## View Integration

### In CreateSurveyFormView

```python
def get(self, request, *args, **kwargs):
    # Check for draft
    draft = DraftService.load_draft(
        survey=self.survey,
        user=request.user if request.user.is_authenticated else None,
        session_key=request.session.session_key
    )
    
    if draft and request.GET.get('resume_draft'):
        # Load draft data
        form_data = DraftService.get_draft_data_for_form(draft)
        form = self.form_class(initial=form_data)
        context['current_section'] = draft.current_section
        context['has_draft'] = True
    
    return render(request, self.template_name, context)

def post(self, request, *args, **kwargs):
    form = self.form_class(request.POST, request.FILES)
    
    if 'save_draft' in request.POST:
        # Save draft
        answers = DraftService.extract_answers_from_form(form.data)
        DraftService.save_draft(
            survey=self.survey,
            data=answers,
            user=request.user if request.user.is_authenticated else None,
            session_key=request.session.session_key,
            current_section=current_section
        )
        messages.success(request, 'Draft saved successfully')
        return redirect('same_page')
    
    if form.is_valid():
        # Final submission
        form.save()
        
        # Delete draft
        DraftService.delete_draft(
            survey=self.survey,
            user=request.user if request.user.is_authenticated else None,
            session_key=request.session.session_key
        )
        
        return redirect('success_page')
```

## Section Navigation with Drafts

When using multi-section surveys:

### Navigation Flow

```
Section 1 → [Next] → Save draft (Section 1 complete)
                   ↓
Section 2 → [Next] → Update draft (Section 2 complete)
                   ↓
Section 3 → [Submit] → Save final response, delete draft
```

### Going Back

```
Section 2 → [Previous] → Load Section 1
                       → Draft data still preserved
                       → Can modify previous answers
```

### Current Section Tracking

Draft always stores current section:

```python
draft.current_section  # Section object user is on
```

When resuming:
- Navigate to current_section
- Pre-fill answers from draft.data
- User can continue or go back

## Expiration and Cleanup

### Expiration Logic

```python
# On save
from datetime import timedelta
from django.utils import timezone

expires_at = timezone.now() + timedelta(days=settings.SURVEY_DRAFT_EXPIRY_DAYS)
draft.expires_at = expires_at
draft.save()
```

Each save refreshes expiration:
- Initial save: Expires in 30 days
- User saves again 10 days later: Expires in 30 days from that point

### Cleanup Command

```bash
python manage.py cleanup_expired_drafts
```

**What it does**:
1. Finds all DraftResponse where expires_at <= now
2. Deletes those drafts
3. Reports count

**Output**:
```
Cleaning up expired drafts...
Successfully deleted 15 expired draft(s)
```

### Automated Cleanup

Add to crontab:

```bash
# Daily at 3 AM
0 3 * * * cd /path/to/project && source venv/bin/activate && python manage.py cleanup_expired_drafts >> /var/log/draft_cleanup.log 2>&1
```

### Manual Cleanup

In admin interface:
1. Go to **Admin → Draft Responses**
2. Select expired drafts
3. Action: "Delete selected draft responses"

## Security Considerations

### Access Control

**Authenticated Users**:
- Draft linked to user ID
- Only that user can access/resume
- Secure across devices

**Anonymous Users**:
- Draft linked to session key
- Only same browser session can access
- Not secure across devices
- Session hijacking risk (use HTTPS)

### Data Privacy

Drafts contain partial responses:
- Same privacy rules as final responses
- Include in GDPR data exports
- Delete on user account deletion
- Expire automatically

### Session Security

```python
# settings.py - Production settings
SESSION_COOKIE_SECURE = True      # HTTPS only
SESSION_COOKIE_HTTPONLY = True    # No JavaScript access
SESSION_COOKIE_SAMESITE = 'Lax'   # CSRF protection
```

## Limitations

### 1. File Uploads

**Files NOT saved in drafts**:
- File inputs appear in draft form
- User must re-upload files when resuming
- Files only saved on final submission

**Reason**: 
- Avoid orphaned files
- Simplify draft expiration
- Reduce storage usage

### 2. Anonymous User Sessions

**Session dependencies**:
- Requires browser cookies enabled
- Clears if browser session ends
- Not portable across devices

**Workaround**: Encourage user login for long surveys

### 3. Survey Changes

**If survey edited after draft created**:
- Questions deleted: Answers orphaned (ignored)
- Questions added: Not in draft (shown empty)
- Questions reordered: Draft still works
- Sections reorganized: current_section may be invalid

**Best practice**: Avoid editing live surveys with active drafts

### 4. Concurrent Edits

**Multiple devices (authenticated)**:
- Last save wins
- No conflict resolution
- Draft from Device A overwritten by Device B

**Workaround**: Show last_updated timestamp, warn user

## Monitoring

### Database Queries

Check draft counts:

```python
from djf_surveys.models import DraftResponse
from django.utils import timezone

# Total drafts
total = DraftResponse.objects.count()

# Active (not expired)
active = DraftResponse.objects.filter(expires_at__gt=timezone.now()).count()

# Expired (ready for cleanup)
expired = DraftResponse.objects.filter(expires_at__lte=timezone.now()).count()

# Per survey
per_survey = DraftResponse.objects.values('survey__name').annotate(count=Count('id'))
```

### Storage Impact

```sql
-- Average draft size
SELECT AVG(LENGTH(data)) as avg_size 
FROM djf_surveys_draftresponse;

-- Largest drafts
SELECT id, survey_id, LENGTH(data) as size
FROM djf_surveys_draftresponse
ORDER BY size DESC
LIMIT 10;
```

### Metrics to Track

- Total active drafts
- Expired drafts pending cleanup
- Average time between draft save and final submit
- Draft completion rate (drafts → final submissions)
- Storage usage by drafts

## Troubleshooting

### Draft Not Saving

**Check**:
1. Session exists: `request.session.session_key`
2. No exceptions in view
3. Database writable
4. User or session_key provided

**Debug**:
```python
# In view
print(f"User: {request.user}")
print(f"Session: {request.session.session_key}")
print(f"Draft data: {draft_data}")
```

### Resume Not Working

**Check**:
1. Draft exists and not expired
2. URL parameter correct: `?resume_draft=1`
3. Session key matches (anonymous users)
4. User matches (authenticated users)

**Debug**:
```python
draft = DraftService.load_draft(survey, user=request.user)
print(f"Draft found: {draft}")
if draft:
    print(f"Expires: {draft.expires_at}")
    print(f"Current section: {draft.current_section}")
```

### Expired Drafts Not Deleted

**Check**:
1. Cron job running
2. Command permissions
3. Virtual environment activated in cron
4. Log file permissions

**Manual test**:
```bash
python manage.py cleanup_expired_drafts
```

### Draft Data Mismatch

**Symptoms**: Form shows wrong data when resuming

**Causes**:
1. Survey questions changed
2. Question IDs don't match
3. Data corruption in JSON field

**Solution**:
```python
# In admin, inspect draft data
draft = DraftResponse.objects.get(id=123)
print(draft.data)  # Should be dict of question_id: value

# Fix if needed
draft.data = {15: "corrected value"}
draft.save()
```

## Testing

### Unit Tests

```python
from djf_surveys.models import DraftResponse, Survey
from djf_surveys.draft_service import DraftService

def test_save_and_load_draft():
    # Save
    draft = DraftService.save_draft(
        survey=survey,
        data={1: "answer"},
        user=user
    )
    assert draft.id
    
    # Load
    loaded = DraftService.load_draft(survey, user=user)
    assert loaded.id == draft.id
    assert loaded.data[1] == "answer"

def test_draft_expiration():
    # Create expired draft
    draft = DraftResponse.objects.create(
        survey=survey,
        user=user,
        data={},
        expires_at=timezone.now() - timedelta(days=1)
    )
    
    # Should not load
    loaded = DraftService.load_draft(survey, user=user)
    assert loaded is None
    
    # Should be cleaned up
    DraftService.cleanup_expired_drafts()
    assert not DraftResponse.objects.filter(id=draft.id).exists()
```

### Integration Tests

```python
def test_draft_workflow(client, user, survey):
    client.login(username='testuser', password='password')
    
    # Start survey
    response = client.get(f'/surveys/{survey.slug}/')
    assert response.status_code == 200
    
    # Save draft
    response = client.post(f'/surveys/{survey.slug}/', {
        'field_survey_1': 'Test answer',
        'save_draft': '1'
    })
    assert response.status_code == 302
    
    # Verify draft created
    draft = DraftResponse.objects.filter(survey=survey, user=user).first()
    assert draft
    assert draft.data['1'] == 'Test answer'
    
    # Resume draft
    response = client.get(f'/surveys/{survey.slug}/?resume_draft=1')
    assert b'Test answer' in response.content
    
    # Final submit
    response = client.post(f'/surveys/{survey.slug}/', {
        'field_survey_1': 'Final answer',
        'submit': '1'
    })
    
    # Draft should be deleted
    assert not DraftResponse.objects.filter(id=draft.id).exists()
```

## Best Practices

### 1. Clear Communication

Tell users:
- When drafts are auto-saved
- How long drafts are kept
- How to resume

### 2. Appropriate Expiration

- Short surveys (< 5 min): 7 days
- Medium surveys (5-15 min): 30 days
- Long surveys (> 15 min): 90 days

### 3. Cleanup Schedule

Run cleanup daily:
- Low traffic times (e.g., 3 AM)
- Log results
- Monitor for issues

### 4. User Feedback

Show:
- "Draft saved" confirmation
- "Draft updated" on subsequent saves
- Last saved timestamp
- Expiration warning if approaching

### 5. Data Migration

When exporting survey data:
- Include active drafts (partial responses)
- Mark as "incomplete"
- Respect expiration dates

## See Also

- **Section Guide**: Multi-section surveys with drafts
- **Cron Setup**: `CRON_SETUP.md` - Automated cleanup
- **Admin Guide**: `ADMIN_GUIDE.md` - Managing drafts
- **Code**: `djf_surveys/draft_service.py` - Implementation
