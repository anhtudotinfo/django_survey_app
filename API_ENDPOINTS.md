# Survey Application API Endpoints

## Overview

This document describes all HTTP endpoints in the Django Survey Application, including the new endpoints added for sections, file uploads, and draft management.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://yourdomain.com`

---

## Table of Contents

1. [Public Survey Endpoints](#public-survey-endpoints)
2. [User Authentication](#user-authentication)
3. [Survey Response Management](#survey-response-management)
4. [File Management](#file-management)
5. [Draft Management](#draft-management)
6. [Admin Endpoints](#admin-endpoints)
7. [Static Content](#static-content)

---

## Public Survey Endpoints

### List All Surveys

**GET** `/surveys/`

Lists all available surveys.

**Query Parameters:**
- None

**Response:**
- Status: `200 OK`
- Content: HTML page with list of surveys

**Authentication:** Not required (unless `can_anonymous_user=False` for specific surveys)

---

### View Survey Form

**GET** `/surveys/<slug>/`

Display survey form for filling out.

**URL Parameters:**
- `slug` (string): Survey slug identifier

**Query Parameters:**
- `section` (integer, optional): Section ID to display (default: first section)
- `resume_draft` (boolean, optional): Load saved draft (`?resume_draft=1`)
- `discard_draft` (boolean, optional): Discard saved draft and start fresh (`?discard_draft=1`)

**Response:**
- Status: `200 OK` - Survey form displayed
- Status: `404 Not Found` - Survey doesn't exist
- Status: `403 Forbidden` - User not authorized (if anonymous users not allowed)

**Features:**
- **Multi-section support**: Shows questions from current section only
- **Progress tracking**: Displays section X of Y with progress bar
- **Draft resume**: Shows banner if draft exists
- **Navigation**: Previous/Next/Submit buttons based on section position

**Example:**
```
GET /surveys/customer-feedback/
GET /surveys/customer-feedback/?section=2
GET /surveys/customer-feedback/?resume_draft=1
```

---

### Submit Survey Response

**POST** `/surveys/<slug>/`

Submit answers for current section or final survey.

**URL Parameters:**
- `slug` (string): Survey slug identifier

**Request Body (form-data):**
- `field_survey_{question_id}`: Answer value for each question
- `action`: `next` | `previous` | `submit` | `save_draft`
- `current_section` (hidden): Current section ID
- File uploads (if file-type questions exist)

**Response:**

**On Success (Final Submit):**
- Status: `302 Found`
- Redirect: `/surveys/<slug>/success/`
- Draft deleted (if exists)

**On Save Draft:**
- Status: `302 Found`
- Redirect: Same page with success message
- Draft saved/updated

**On Section Navigation:**
- Status: `302 Found`
- Redirect: Next/previous section
- Answers saved to draft (if enabled)

**On Validation Error:**
- Status: `200 OK`
- Content: Form with error messages
- Previous answers preserved

**Example:**
```http
POST /surveys/customer-feedback/
Content-Type: multipart/form-data

field_survey_1=John Doe
field_survey_2=john@example.com
field_survey_3=Yes
action=next
current_section=1
```

**Branch Logic:**
After submitting section, system evaluates branch rules:
1. Check all rules for current section (ordered by priority)
2. If rule matches, navigate to `next_section` in rule
3. If no rules match, navigate to next sequential section
4. If `next_section` is `null`, end survey

---

### Survey Success Page

**GET** `/surveys/<slug>/success/`

Confirmation page after successful survey submission.

**URL Parameters:**
- `slug` (string): Survey slug identifier

**Response:**
- Status: `200 OK`
- Content: Custom success message (from `Survey.success_page_content`) or default

**Authentication:** Not required

---

### View Survey Details

**GET** `/surveys/<slug>/detail/`

View details of a submitted survey response.

**URL Parameters:**
- `slug` (string): Survey slug identifier

**Query Parameters:**
- `user_answer_id` (integer, required): UserAnswer ID to view

**Response:**
- Status: `200 OK` - Response details displayed
- Status: `403 Forbidden` - Not authorized to view
- Status: `404 Not Found` - Response doesn't exist

**Authorization:**
- Response owner can view
- Admin users can view all
- If `private_response=True`, only owner and admin can view

**Example:**
```
GET /surveys/customer-feedback/detail/?user_answer_id=123
```

---

## User Authentication

### Login

**GET/POST** `/accounts/login/`

User login page.

**POST Parameters:**
- `username` (string): Username or email
- `password` (string): Password
- `next` (optional): Redirect URL after login

**Response:**
- Status: `302 Found` - Redirect to `next` or home
- Status: `200 OK` - Login form with errors

---

### Logout

**GET** `/accounts/logout/`

Log out current user.

**Response:**
- Status: `302 Found`
- Redirect: Home page or login

---

### Register

**GET/POST** `/accounts/register/`

User registration page.

**POST Parameters:**
- `username` (string)
- `email` (string)
- `password1` (string)
- `password2` (string): Confirmation

**Response:**
- Status: `302 Found` - Redirect to login on success
- Status: `200 OK` - Registration form with errors

---

## Survey Response Management

### Edit Response

**GET/POST** `/surveys/<slug>/edit/`

Edit a previously submitted response.

**Requirements:**
- User must be authenticated
- Survey must have `editable=True`
- User must be owner of response

**URL Parameters:**
- `slug` (string): Survey slug identifier

**Query Parameters:**
- `user_answer_id` (integer, required): Response ID to edit

**POST Parameters:**
- Same as submit survey
- Existing file uploads preserved unless new file uploaded

**Response:**
- Status: `200 OK` - Edit form
- Status: `302 Found` - Redirect on success
- Status: `403 Forbidden` - Not allowed to edit

**Example:**
```
GET /surveys/customer-feedback/edit/?user_answer_id=123
```

**Sections Support:**
- Can navigate between sections
- Branch logic re-evaluated on edit
- Draft not used (editing existing response)

---

### Delete Response

**POST** `/surveys/<slug>/delete/`

Delete a survey response.

**Requirements:**
- User must be authenticated
- Survey must have `deletable=True`
- User must be owner of response

**URL Parameters:**
- `slug` (string): Survey slug identifier

**POST Parameters:**
- `user_answer_id` (integer): Response ID to delete

**Response:**
- Status: `302 Found` - Redirect to survey list
- Status: `403 Forbidden` - Not allowed to delete

**Side Effects:**
- Deletes all Answer records
- Deletes uploaded files
- Deletes UserAnswer record

---

## File Management

### Download Uploaded File

**GET** `/surveys/download/<answer_id>/`

Download a file uploaded in a survey response.

**URL Parameters:**
- `answer_id` (integer): Answer ID containing file

**Response:**
- Status: `200 OK` - File download
- Status: `403 Forbidden` - Not authorized
- Status: `404 Not Found` - File doesn't exist

**Authorization:**
- Response owner can download
- Admin users can download all
- Anonymous users cannot download (even if they submitted)

**Security:**
- Files served through Django view (not direct access)
- Permission check before serving
- Filename sanitized

**Example:**
```
GET /surveys/download/456/
```

**Response Headers:**
```http
Content-Type: application/pdf
Content-Disposition: attachment; filename="resume.pdf"
```

**Supported File Types:**
- Images: jpg, jpeg, png, gif, webp
- Documents: pdf, doc, docx, txt
- Spreadsheets: xls, xlsx, csv
- Archives: zip, rar

**File Location:**
```
media/survey_uploads/{survey_id}/{user_answer_id}/{filename}
```

---

## Draft Management

### Save Draft (Implicit)

**POST** `/surveys/<slug>/`

Save draft is handled by the main survey submission endpoint.

**Action Parameter:**
- `action=save_draft`

**Behavior:**
- Creates or updates DraftResponse record
- Stores question answers in JSON field
- Sets current_section
- Extends expiration date
- Does NOT save file uploads (files only saved on final submit)

**User Identification:**
- Authenticated: Linked to User ID
- Anonymous: Linked to Session Key

**Example:**
```http
POST /surveys/customer-feedback/
Content-Type: application/x-www-form-urlencoded

field_survey_1=John
field_survey_2=john@example.com
action=save_draft
current_section=1
```

---

### Load Draft (Implicit)

**GET** `/surveys/<slug>/?resume_draft=1`

Loads saved draft when accessing survey.

**Behavior:**
- Looks up DraftResponse by user/session and survey
- Pre-fills form with saved answers
- Navigates to `current_section` from draft
- Shows draft banner with timestamp

**Expiration:**
- Drafts expire after `SURVEY_DRAFT_EXPIRY_DAYS` (default 30 days)
- Expired drafts not loaded
- Expired drafts cleaned by cron job

---

### Discard Draft

**GET** `/surveys/<slug>/?discard_draft=1`

Deletes saved draft and starts fresh.

**Behavior:**
- Deletes DraftResponse record
- Redirects to survey start (section 1)
- No data pre-filled

---

## Admin Endpoints

### Admin Interface

**GET** `/moi-admin/`

Django admin interface for managing surveys, sections, questions, responses.

**Authentication:** Requires staff/admin user

**Available Models:**
- Surveys
- Sections (NEW)
- Questions
- Branch Rules (NEW)
- Draft Responses (NEW)
- User Answers
- Answers
- Directions

**Actions:**
- Create, read, update, delete
- Inline editing for related models
- Filtering and search
- Export responses (custom action)

---

### Survey Export

**POST** `/moi-admin/djf_surveys/survey/<id>/change/`

Export survey responses to CSV.

**Action:** Select "Export responses to CSV" from admin actions

**Response:**
- Status: `200 OK`
- Content-Type: `text/csv`
- Content-Disposition: `attachment; filename="survey_responses_<slug>.csv"`

**CSV Format:**
```csv
Response ID,User,Created At,Question 1,Question 2,...
1,john@example.com,2025-01-15,Answer 1,Answer 2,...
2,jane@example.com,2025-01-16,Answer 1,Answer 2,...
```

**File Uploads in CSV:**
- Shows filename (not downloadable from CSV)
- Actual files stored in `media/survey_uploads/`

---

## Static Content

### Media Files

**GET** `/media/<path>`

**Development Only**: Django serves media files directly

**Production**: Should be served by web server (Nginx/Apache)

**URL Examples:**
```
/media/survey_uploads/5/123/document.pdf
/media/user_image/default.png
```

**Security:**
- Survey uploads NOT directly accessible
- Must use `/surveys/download/<answer_id>/` endpoint
- Permission check enforced

---

### Static Files

**GET** `/static/<path>`

CSS, JavaScript, images for application UI.

**Examples:**
```
/static/css/main.css
/static/js/survey.js
/static/images/logo.png
```

---

## Response Status Codes

### Success Codes

- `200 OK` - Request successful, content returned
- `302 Found` - Redirect (after form submission, login, etc.)

### Client Error Codes

- `400 Bad Request` - Invalid form data
- `403 Forbidden` - Not authorized to access resource
- `404 Not Found` - Resource doesn't exist
- `405 Method Not Allowed` - Wrong HTTP method

### Server Error Codes

- `500 Internal Server Error` - Server error (check logs)

---

## Rate Limiting

Currently no rate limiting implemented.

**Recommendations for Production:**
- Implement rate limiting for survey submissions
- Prevent spam and abuse
- Use Django middleware or reverse proxy (Nginx)

**Example (django-ratelimit):**
```python
from ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='10/h', method='POST')
def submit_survey(request):
    # ...
```

---

## CORS Policy

Default: Same-origin only

If building API for external clients:
```python
# settings.py
INSTALLED_APPS += ['corsheaders']

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    # ...
]

CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
]
```

---

## Webhooks / Notifications

### Email Notifications

When survey submitted, email sent to addresses in `Survey.notification_to`:

**Trigger:** Survey final submission

**Content:**
- Survey name
- Submitter info (if available)
- Submission timestamp
- Link to view response (admin)

**Configuration:**
```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-password'
```

---

## Error Responses

### Validation Error Example

```http
POST /surveys/example/
```

**Response (200 OK):**
```html
<form>
  <div class="error">This field is required</div>
  <input name="field_survey_1" value="">
  ...
</form>
```

### Authorization Error Example

```http
GET /surveys/private-survey/
```

**Response (403 Forbidden):**
```html
<h1>Permission Denied</h1>
<p>You must be logged in to access this survey.</p>
```

### Not Found Example

```http
GET /surveys/nonexistent/
```

**Response (404 Not Found):**
```html
<h1>Survey Not Found</h1>
<p>The survey you're looking for doesn't exist.</p>
```

---

## Pagination

Currently no pagination on public survey list.

**For large deployments**, consider adding:
```python
# views.py
from django.core.paginator import Paginator

surveys = Survey.objects.all()
paginator = Paginator(surveys, 10)  # 10 per page
page_surveys = paginator.get_page(request.GET.get('page'))
```

---

## Search / Filtering

**Admin Interface:**
- Search surveys by name, slug, description
- Filter by created date, settings
- Filter questions by survey, section, type

**Public Interface:**
- Currently no search implemented
- All surveys listed

**To add search:**
```html
<form method="get">
  <input type="text" name="q" placeholder="Search surveys...">
  <button type="submit">Search</button>
</form>
```

```python
# views.py
query = request.GET.get('q')
if query:
    surveys = Survey.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query)
    )
```

---

## Versioning

API versioning not currently implemented.

**If needed**, use URL-based versioning:
```
/api/v1/surveys/
/api/v2/surveys/
```

Or header-based:
```http
Accept: application/json; version=1
```

---

## RESTful API (Future)

Current app is primarily HTML-based (Django templates).

**To add REST API:**

Install Django REST Framework:
```bash
pip install djangorestframework
```

Create serializers and viewsets:
```python
# serializers.py
from rest_framework import serializers
from djf_surveys.models import Survey, Section, Question

class SurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = '__all__'

# views.py
from rest_framework import viewsets

class SurveyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
```

**Endpoints would be:**
```
GET /api/surveys/
GET /api/surveys/{id}/
GET /api/surveys/{id}/sections/
POST /api/surveys/{id}/responses/
```

---

## Testing Endpoints

### Manual Testing (curl)

**View survey:**
```bash
curl http://localhost:8000/surveys/example/
```

**Submit survey:**
```bash
curl -X POST http://localhost:8000/surveys/example/ \
  -d "field_survey_1=Answer" \
  -d "action=submit" \
  -b cookies.txt -c cookies.txt
```

**Download file:**
```bash
curl -b cookies.txt http://localhost:8000/surveys/download/123/ -o file.pdf
```

### Automated Testing

Use Django test client:
```python
from django.test import Client

client = Client()
response = client.get('/surveys/example/')
assert response.status_code == 200

response = client.post('/surveys/example/', {
    'field_survey_1': 'Answer',
    'action': 'submit'
})
assert response.status_code == 302
```

---

## Security Headers

**Recommended production headers:**

```python
# settings.py
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_SSL_REDIRECT = True  # Force HTTPS
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

**Content Security Policy:**
```python
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
```

---

## Monitoring & Logging

**Log survey submissions:**
```python
import logging
logger = logging.getLogger('djf_surveys')

logger.info(f'Survey submitted: {survey.name} by {user}')
logger.warning(f'Failed survey validation: {survey.name}')
logger.error(f'Error saving file: {e}')
```

**Monitor endpoints:**
- Response times
- Error rates
- File upload sizes
- Draft save frequency

**Tools:**
- Django Debug Toolbar (development)
- Sentry (error tracking)
- Prometheus + Grafana (metrics)
- ELK Stack (log aggregation)

---

## Performance Optimization

**Query Optimization:**
```python
# Use select_related for foreign keys
surveys = Survey.objects.select_related('direction').all()

# Use prefetch_related for many-to-many
surveys = Survey.objects.prefetch_related('sections__questions').all()
```

**Caching:**
```python
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # Cache for 15 minutes
def survey_list(request):
    # ...
```

**Database Indexes:**
```python
class Meta:
    indexes = [
        models.Index(fields=['survey', 'ordering']),
        models.Index(fields=['user', 'survey']),
    ]
```

---

## Changelog

### Version 2.0 (Current)
- ✅ Added multi-section surveys
- ✅ Added branch logic/conditional navigation
- ✅ Added file upload question type
- ✅ Added draft save/resume functionality
- ✅ Added file download endpoint with access control
- ✅ Added draft management

### Version 1.0 (Previous)
- Basic single-page surveys
- User authentication
- Admin interface
- Response viewing and editing

---

## Support & Documentation

- **User Guide**: See `README.md`
- **Admin Guide**: See `ADMIN_GUIDE.md` and `SECTION_BRANCH_ADMIN_GUIDE.md`
- **Branch Logic**: See `BRANCH_LOGIC_GUIDE.md`
- **File Uploads**: See `FILE_UPLOAD_GUIDE.md`
- **Drafts**: See `DRAFT_SYSTEM_GUIDE.md`
- **Cron Jobs**: See `CRON_SETUP.md`
- **Security**: See `SECURITY_REVIEW.md`

**Issue Reporting:**
- GitHub Issues: [your-repo-url]
- Email: [support-email]

**API Questions:**
- Check documentation first
- Review code in `djf_surveys/views.py`
- Test in development environment
- Contact development team
