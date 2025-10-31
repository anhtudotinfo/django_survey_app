# Django Survey Application - Documentation Index

## Overview

Complete documentation for the Django Survey Application with multi-section surveys, branch logic, file uploads, and draft save/resume functionality.

---

## Quick Start

**New to the application?** Start here:

1. **[README.md](README.md)** - Project overview and quick start
2. **[ADMIN_GUIDE.md](ADMIN_GUIDE.md)** - Admin interface basics
3. **[SECTION_BRANCH_ADMIN_GUIDE.md](SECTION_BRANCH_ADMIN_GUIDE.md)** - Creating multi-section surveys

**Need something specific?** See categories below.

---

## Documentation Categories

### 📚 For Administrators

**Setting Up Surveys:**
- **[ADMIN_GUIDE.md](ADMIN_GUIDE.md)** - Complete admin interface guide
- **[SECTION_BRANCH_ADMIN_GUIDE.md](SECTION_BRANCH_ADMIN_GUIDE.md)** - Detailed section and branch logic setup
  - Creating multi-section surveys
  - Setting up conditional navigation
  - Common scenarios and examples
  - Testing and troubleshooting

**Feature Guides:**
- **[BRANCH_LOGIC_GUIDE.md](BRANCH_LOGIC_GUIDE.md)** - Branch logic concepts and usage
  - How branch rules work
  - Operator types (equals, contains, in)
  - Example configurations
  - Best practices and debugging

- **[FILE_UPLOAD_GUIDE.md](FILE_UPLOAD_GUIDE.md)** - File upload configuration and management
  - Allowed file types and size limits
  - Security features
  - Storage configuration
  - File cleanup

- **[DRAFT_SYSTEM_GUIDE.md](DRAFT_SYSTEM_GUIDE.md)** - Draft save/resume functionality
  - How drafts work for users
  - Configuration options
  - Data storage and expiration
  - Testing and troubleshooting

**Maintenance:**
- **[CRON_SETUP.md](CRON_SETUP.md)** - Automated cleanup tasks
  - Setting up cron jobs
  - Cleanup commands
  - Monitoring and alerts
  - Alternative schedulers (systemd)

---

### 👨‍💻 For Developers

**Code Documentation:**
- **In-code docstrings** - See `djf_surveys/models.py` for:
  - `Section` model documentation
  - `DraftResponse` model documentation
  - `BranchRule` model documentation
  - All model fields and methods

**Technical Guides:**
- **[API_ENDPOINTS.md](API_ENDPOINTS.md)** - All HTTP endpoints
  - Public survey endpoints
  - File download endpoints
  - Draft management
  - Admin endpoints
  - Response codes and examples

- **[BRANCH_LOGIC_GUIDE.md](BRANCH_LOGIC_GUIDE.md)** - Implementation details
  - `BranchEvaluator` class usage
  - Rule evaluation algorithm
  - Integration points

- **[FILE_UPLOAD_GUIDE.md](FILE_UPLOAD_GUIDE.md)** - File handling implementation
  - Validators (`FileTypeValidator`, `FileSizeValidator`)
  - Upload path generation
  - Security measures
  - Storage backends (local, S3, GCS)

- **[DRAFT_SYSTEM_GUIDE.md](DRAFT_SYSTEM_GUIDE.md)** - Draft service API
  - `DraftService` class methods
  - Data structure and storage
  - Integration with views

**Architecture Documents:**
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Implementation overview
- **[IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md)** - Current status
- **[PROJECT_STATUS.md](PROJECT_STATUS.md)** - Project status and milestones

---

### 🔒 For Security/Operations

**Security:**
- **[SECURITY_REVIEW.md](SECURITY_REVIEW.md)** - Comprehensive security analysis
  - File upload security
  - Access control
  - Data privacy
  - Recommendations

- **[SECURITY_WARNINGS.md](SECURITY_WARNINGS.md)** - Security warnings and mitigations

**Operations:**
- **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** - Pre-deployment checklist
- **[CRON_SETUP.md](CRON_SETUP.md)** - Automated maintenance tasks
- **[API_ENDPOINTS.md](API_ENDPOINTS.md)** - Endpoint reference for monitoring

---

### 🧪 For QA/Testing

**Testing Documentation:**
- **[TESTING_COMPLETE.md](TESTING_COMPLETE.md)** - Test results summary
- **[TEST_RESULTS.md](TEST_RESULTS.md)** - Detailed test results
- **[MANUAL_QA_PLAN.md](MANUAL_QA_PLAN.md)** - Manual testing procedures

**Test Files:**
- **test_implementation.py** - Integration tests
- **test_file_upload.py** - File upload tests
- **djf_surveys/tests.py** - Unit tests

**Testing Guides:**
- **[SECTION_BRANCH_ADMIN_GUIDE.md](SECTION_BRANCH_ADMIN_GUIDE.md)** - Section "Testing Your Setup"
- **[BRANCH_LOGIC_GUIDE.md](BRANCH_LOGIC_GUIDE.md)** - Section "Debugging Tips"

---

## Feature Documentation Matrix

| Feature | User Guide | Admin Setup | Developer Docs | Testing |
|---------|-----------|-------------|----------------|---------|
| **Multi-Section Surveys** | - | [SECTION_BRANCH_ADMIN_GUIDE.md](SECTION_BRANCH_ADMIN_GUIDE.md) | models.py (Section) | test_implementation.py |
| **Branch Logic** | - | [SECTION_BRANCH_ADMIN_GUIDE.md](SECTION_BRANCH_ADMIN_GUIDE.md) | [BRANCH_LOGIC_GUIDE.md](BRANCH_LOGIC_GUIDE.md) | test_implementation.py |
| **File Uploads** | [FILE_UPLOAD_GUIDE.md](FILE_UPLOAD_GUIDE.md) | [ADMIN_GUIDE.md](ADMIN_GUIDE.md) | [FILE_UPLOAD_GUIDE.md](FILE_UPLOAD_GUIDE.md) | test_file_upload.py |
| **Draft System** | [DRAFT_SYSTEM_GUIDE.md](DRAFT_SYSTEM_GUIDE.md) | - | [DRAFT_SYSTEM_GUIDE.md](DRAFT_SYSTEM_GUIDE.md) | test_implementation.py |
| **File Download** | [FILE_UPLOAD_GUIDE.md](FILE_UPLOAD_GUIDE.md) | - | [API_ENDPOINTS.md](API_ENDPOINTS.md) | test_file_upload.py |
| **Cleanup Commands** | - | [CRON_SETUP.md](CRON_SETUP.md) | [CRON_SETUP.md](CRON_SETUP.md) | Manual testing |

---

## Common Tasks

### I want to...

**...create a simple survey**
1. Read [ADMIN_GUIDE.md](ADMIN_GUIDE.md) - "Workflow quản lý Survey"
2. Log into admin interface
3. Create survey, add questions
4. Test at `/surveys/<slug>/`

**...create a multi-section survey**
1. Read [SECTION_BRANCH_ADMIN_GUIDE.md](SECTION_BRANCH_ADMIN_GUIDE.md) - "Creating Multi-Section Surveys"
2. Create survey
3. Add sections with ordering
4. Assign questions to sections
5. Test navigation

**...add conditional navigation (skip logic)**
1. Read [SECTION_BRANCH_ADMIN_GUIDE.md](SECTION_BRANCH_ADMIN_GUIDE.md) - "Setting Up Branch Logic"
2. Read [BRANCH_LOGIC_GUIDE.md](BRANCH_LOGIC_GUIDE.md) for concepts
3. Create sections and questions
4. Add branch rules with conditions
5. Test all paths

**...allow file uploads**
1. Read [FILE_UPLOAD_GUIDE.md](FILE_UPLOAD_GUIDE.md) - "Configuration"
2. Configure `settings.py` (MEDIA_ROOT, allowed types, max size)
3. Create question with type "File Upload"
4. Test upload and download

**...enable draft save/resume**
1. Read [DRAFT_SYSTEM_GUIDE.md](DRAFT_SYSTEM_GUIDE.md)
2. Configure `SURVEY_DRAFT_EXPIRY_DAYS` in settings
3. Enable sections (drafts work with section navigation)
4. Test save/resume flow

**...set up automated cleanup**
1. Read [CRON_SETUP.md](CRON_SETUP.md)
2. Test commands manually
3. Add to crontab or systemd
4. Monitor logs

**...understand security**
1. Read [SECURITY_REVIEW.md](SECURITY_REVIEW.md)
2. Read [FILE_UPLOAD_GUIDE.md](FILE_UPLOAD_GUIDE.md) - "Security Features"
3. Review settings in production checklist

**...deploy to production**
1. Read [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
2. Run tests: `python manage.py test`
3. Configure production settings
4. Run migrations
5. Set up cron jobs
6. Monitor logs

**...troubleshoot an issue**
- Branch not triggering: [BRANCH_LOGIC_GUIDE.md](BRANCH_LOGIC_GUIDE.md) - "Debugging Tips"
- File upload failing: [FILE_UPLOAD_GUIDE.md](FILE_UPLOAD_GUIDE.md) - "Troubleshooting"
- Draft not saving: [DRAFT_SYSTEM_GUIDE.md](DRAFT_SYSTEM_GUIDE.md) - "Troubleshooting"
- Section issues: [SECTION_BRANCH_ADMIN_GUIDE.md](SECTION_BRANCH_ADMIN_GUIDE.md) - "Troubleshooting"

**...understand the code**
1. Read models: `djf_surveys/models.py` (has docstrings)
2. Read services: `djf_surveys/draft_service.py`, `djf_surveys/branch_logic.py`
3. Read views: `djf_surveys/views.py`
4. Read API docs: [API_ENDPOINTS.md](API_ENDPOINTS.md)

**...write tests**
1. Review existing: `test_implementation.py`, `test_file_upload.py`
2. Read Django testing docs
3. Test checklist in [SECTION_BRANCH_ADMIN_GUIDE.md](SECTION_BRANCH_ADMIN_GUIDE.md)

---

## File Organization

```
django_survey_app/
│
├── Documentation (You are here!)
│   ├── DOCUMENTATION_INDEX.md ← THIS FILE
│   ├── README.md - Project overview
│   ├── ADMIN_GUIDE.md - Admin interface basics
│   ├── SECTION_BRANCH_ADMIN_GUIDE.md - Detailed section/branch setup
│   ├── BRANCH_LOGIC_GUIDE.md - Branch logic concepts
│   ├── FILE_UPLOAD_GUIDE.md - File upload guide
│   ├── DRAFT_SYSTEM_GUIDE.md - Draft system guide
│   ├── API_ENDPOINTS.md - API reference
│   ├── CRON_SETUP.md - Cron job setup
│   ├── SECURITY_REVIEW.md - Security analysis
│   ├── DEPLOYMENT_CHECKLIST.md - Deployment guide
│   ├── TESTING_COMPLETE.md - Test results
│   └── [Other docs...]
│
├── Application Code
│   ├── djf_surveys/
│   │   ├── models.py - Data models (with docstrings)
│   │   ├── views.py - View logic
│   │   ├── forms.py - Form handling
│   │   ├── admin.py - Admin configuration
│   │   ├── draft_service.py - Draft management
│   │   ├── branch_logic.py - Branch evaluation
│   │   ├── navigation.py - Section navigation
│   │   ├── validators.py - File validators
│   │   ├── utils.py - Utilities
│   │   ├── tests.py - Unit tests
│   │   ├── management/commands/ - Cleanup commands
│   │   └── templates/ - HTML templates
│   │
│   ├── moi/ - Project settings
│   ├── accounts/ - User management
│   └── manage.py - Django management
│
└── Test Files
    ├── test_implementation.py - Integration tests
    └── test_file_upload.py - File upload tests
```

---

## Glossary

**Survey** - A collection of questions users fill out

**Section** - A group of questions shown on one page (multi-step surveys)

**Question** - Individual question in a survey (11 types including file upload)

**Answer** - User's response to a question

**UserAnswer** - Collection of all answers for one survey submission

**Branch Rule** - Conditional navigation rule (if answer X, go to section Y)

**Draft Response** - Saved partial survey response (save/resume functionality)

**Ordering** - Numeric field determining display sequence

**Priority** - Numeric field determining branch rule evaluation order (lower = higher priority)

**Condition Question** - Question whose answer is checked by branch rule

**Next Section** - Target section if branch rule matches (null = end survey)

**Operator** - Comparison type (equals, not_equals, contains, in)

**Session Key** - Identifier for anonymous user sessions

**File Upload** - Question type allowing file attachments

**Cleanup Commands** - Management commands for maintenance
  - `cleanup_expired_drafts` - Delete old drafts
  - `cleanup_orphaned_files` - Delete unreferenced files

---

## Getting Help

### By Role

**Administrators:**
- Start with [ADMIN_GUIDE.md](ADMIN_GUIDE.md)
- Specific features: See "For Administrators" section above
- Issues: Check troubleshooting sections in relevant guides

**Developers:**
- Code questions: Read in-code docstrings and `djf_surveys/*.py`
- API: See [API_ENDPOINTS.md](API_ENDPOINTS.md)
- Architecture: See implementation docs

**Users (Survey Respondents):**
- Basic usage is intuitive (no docs needed)
- Draft save: See "Save Draft" button in survey
- File upload: Follow on-screen instructions

**QA/Testers:**
- Test plans: See "For QA/Testing" section above
- Test files: `test_*.py` files in root

### Support Channels

1. **Documentation**: Read relevant guide (see matrix above)
2. **Code Comments**: Check `djf_surveys/*.py` docstrings
3. **Troubleshooting Sections**: Each guide has troubleshooting
4. **Issue Tracker**: [GitHub Issues URL if applicable]
5. **Email Support**: [Support email if applicable]

---

## Version History

**Version 2.0** (Current)
- Added multi-section surveys
- Added branch logic
- Added file uploads
- Added draft system
- Comprehensive documentation

**Version 1.0**
- Single-page surveys
- Basic question types
- User authentication
- Admin interface

---

## Contributing to Documentation

### Adding New Documentation

1. Create new .md file in project root
2. Follow existing documentation style
3. Add entry to this index
4. Update relevant cross-references
5. Test all links

### Updating Existing Documentation

1. Update the relevant guide
2. Update version history if major change
3. Check cross-references still work
4. Update "Last Updated" date

### Documentation Style Guide

- Use Markdown format
- Clear headings hierarchy
- Code examples with syntax highlighting
- Cross-reference related docs
- Include troubleshooting sections
- Provide real-world examples

---

## Last Updated

This documentation index: **2025-10-31**

Individual documents may have different update dates. Check each file's header or git history.

---

## Quick Links

**Most Accessed:**
- [Admin Guide](ADMIN_GUIDE.md)
- [Section & Branch Setup](SECTION_BRANCH_ADMIN_GUIDE.md)
- [Branch Logic Concepts](BRANCH_LOGIC_GUIDE.md)
- [File Upload Guide](FILE_UPLOAD_GUIDE.md)
- [API Endpoints](API_ENDPOINTS.md)

**Maintenance:**
- [Cron Setup](CRON_SETUP.md)
- [Security Review](SECURITY_REVIEW.md)
- [Deployment Checklist](DEPLOYMENT_CHECKLIST.md)

**Testing:**
- [Testing Complete](TESTING_COMPLETE.md)
- [Manual QA Plan](MANUAL_QA_PLAN.md)

**Development:**
- Code: `djf_surveys/models.py` (docstrings)
- Tests: `test_implementation.py`, `test_file_upload.py`

---

*For additional help, consult the specific guides listed above or contact the development team.*
