# Implementation Tasks

## 1. Database Models and Migrations

- [x] 1.1 Create Section model with fields: survey (FK), name, description, ordering
- [x] 1.2 Add section (FK) to Question model (nullable for backward compat)
- [x] 1.3 Create DraftResponse model with fields: survey, user, session_key, current_section, data (JSONField), expires_at
- [x] 1.4 Create BranchRule model with fields: section, condition_question, condition_operator, condition_value, next_section, priority
- [x] 1.5 Add file field type to TYPE_FIELD namedtuple (value=10)
- [x] 1.6 Add file_value (FileField) to Answer model
- [x] 1.7 Create migrations for all model changes
- [x] 1.8 Create data migration to create default sections for existing surveys and link existing questions
- [ ] 1.9 Test migrations on copy of production database
- [x] 1.10 Test rollback migrations

## 2. File Upload Infrastructure

- [x] 2.1 Configure MEDIA_ROOT and MEDIA_URL in settings.py
- [x] 2.2 Add file upload settings: SURVEY_FILE_UPLOAD_MAX_SIZE, SURVEY_FILE_ALLOWED_TYPES
- [x] 2.3 Create upload_survey_file function for file path generation
- [x] 2.4 Implement file type validator (check extension and MIME type)
- [x] 2.5 Implement file size validator
- [x] 2.6 Add filename sanitization utility function
- [ ] 2.7 Test file upload with various file types

## 3. Section Management

- [x] 3.1 Add Section admin configuration with list display and ordering
- [x] 3.2 Create inline admin for managing sections within Survey admin
- [x] 3.3 Add section selection to Question admin
- [x] 3.4 Implement section ordering validation (no duplicate orderings)
- [x] 3.5 Add section deletion protection (prevent if contains questions)
- [ ] 3.6 Create management command to reorganize existing surveys into sections (optional helper)
- [ ] 3.7 Test section CRUD operations in admin

## 4. Branch Logic Implementation

- [x] 4.1 Add BranchRule admin with TabularInline in Section admin
- [x] 4.2 Implement operator choices: equals, not_equals, contains, in
- [x] 4.3 Create BranchEvaluator class to evaluate rules against answers
- [x] 4.4 Implement rule priority sorting and first-match logic
- [x] 4.5 Add validation: prevent circular references
- [x] 4.6 Add validation: warn about unreachable sections
- [x] 4.7 Add validation: condition question must be in current or previous section
- [x] 4.8 Add validation: condition value format matches question type
- [ ] 4.9 Test branch evaluation with various scenarios
- [ ] 4.10 Test branch rule validation edge cases

## 5. Survey Form Updates

- [x] 5.1 Update BaseSurveyForm to accept current_section parameter
- [x] 5.2 Modify form to display only questions from current section
- [x] 5.3 Add file upload field handling in form __init__
- [x] 5.4 Implement file field validation in form clean method
- [x] 5.5 Update CreateSurveyForm to handle file uploads in save method
- [x] 5.6 Update EditSurveyForm to pre-fill file field with existing uploads
- [x] 5.7 Add section navigation logic (determine next/previous section)
- [x] 5.8 Integrate BranchEvaluator in navigation logic
- [ ] 5.9 Test form with single section (backward compat)
- [ ] 5.10 Test form with multiple sections and navigation

## 6. Draft Response System

- [x] 6.1 Create DraftService class with methods: save_draft, load_draft, delete_draft
- [x] 6.2 Implement auto-save draft on section navigation
- [x] 6.3 Add manual "Save Draft" button in template
- [x] 6.4 Implement draft loading logic in view dispatch
- [x] 6.5 Show "Resume draft" prompt when draft exists
- [x] 6.6 Handle draft for authenticated users (user FK)
- [x] 6.7 Handle draft for anonymous users (session key)
- [x] 6.8 Set expiration timestamp (default 30 days)
- [x] 6.9 Convert draft to final response on submission
- [ ] 6.10 Test draft save/load/resume flow

## 7. View Layer Updates

- [x] 7.1 Update CreateSurveyFormView to track current section in session/GET param
- [x] 7.2 Add logic to determine first section of survey
- [x] 7.3 Implement section validation before navigation
- [x] 7.4 Add next/previous section navigation handlers
- [x] 7.5 Integrate draft loading in GET request
- [x] 7.6 Integrate draft saving in POST request (before validation)
- [x] 7.7 Update success redirect to clear draft
- [x] 7.8 Create protected file download view with permission checks
- [x] 7.9 Update DetailSurveyView to display file upload answers correctly
- [ ] 7.10 Test view flows with sections and branching

## 8. Template Updates

- [x] 8.1 Create multi-step form template with section container
- [x] 8.2 Add progress bar component showing current section / total
- [x] 8.3 Add step indicator (e.g., "Step 1 of 4")
- [x] 8.4 Implement Previous/Next/Submit button logic
- [x] 8.5 Add "Save Draft" button with AJAX or form action
- [x] 8.6 Create resume draft prompt modal or banner
- [x] 8.7 Update file input styling and filename display
- [ ] 8.8 Add client-side file validation feedback (optional enhancement)
- [x] 8.9 Show section name and description in template
- [ ] 8.10 Test responsive design for mobile devices

## 9. File Management

- [x] 9.1 Implement file serve view with access control
- [x] 9.2 Add file deletion on Answer deletion (signal or override delete)
- [x] 9.3 Create management command for cleanup orphaned files
- [x] 9.4 Create management command for cleanup expired draft files
- [ ] 9.5 Add cron job configuration for scheduled cleanup (documentation)
- [ ] 9.6 Test file permissions and access control
- [x] 9.7 Test file cleanup commands

## 10. Testing

- [x] 10.1 Write unit tests for Section model
- [x] 10.2 Write unit tests for DraftResponse model
- [x] 10.3 Write unit tests for BranchRule model and validation
- [x] 10.4 Write unit tests for BranchEvaluator class
- [x] 10.5 Write unit tests for file validators
- [x] 10.6 Write unit tests for DraftService
- [x] 10.7 Write integration tests for section navigation
- [x] 10.8 Write integration tests for branch logic flows
- [x] 10.9 Write integration tests for draft save/resume
- [x] 10.10 Write integration tests for file upload and download
- [x] 10.11 Test backward compatibility with existing surveys
- [ ] 10.12 Manual QA testing of full user flows

## 11. Documentation

- [x] 11.1 Document Section model in code
- [x] 11.2 Document Branch Logic in README or docs
- [x] 11.3 Document File Upload configuration and security
- [x] 11.4 Document Draft system behavior
- [x] 11.5 Create admin user guide for section and branch setup
- [x] 11.6 Document cleanup commands and cron setup
- [x] 11.7 Update API documentation if endpoints affected
- [x] 11.8 Create documentation index (DOCUMENTATION_INDEX.md)

## 12. Performance and Optimization

- [x] 12.1 Add database indexes: Section.ordering, Question.section, DraftResponse.user, DraftResponse.session_key
- [x] 12.2 Add database indexes: BranchRule.section, BranchRule.priority
- [ ] 12.3 Test query performance with large surveys (>50 questions, >10 sections)
- [ ] 12.4 Implement branch rule caching if needed
- [ ] 12.5 Test file upload performance with max size files
- [ ] 12.6 Monitor database size impact of file uploads

## 13. Security Review

- [ ] 13.1 Verify file upload security (type, size, path validation)
- [ ] 13.2 Verify file access control enforcement
- [ ] 13.3 Verify draft access control (user/session isolation)
- [ ] 13.4 Test for XSS in section name/description display
- [ ] 13.5 Test for SQL injection in branch rule evaluation
- [ ] 13.6 Review file cleanup to prevent data leaks

## 14. Deployment Preparation

- [ ] 14.1 Create deployment checklist
- [ ] 14.2 Prepare rollback plan
- [ ] 14.3 Test migrations on staging environment
- [ ] 14.4 Verify media storage configuration (local/S3)
- [ ] 14.5 Set up monitoring for file storage usage
- [ ] 14.6 Set up monitoring for draft database growth
- [ ] 14.7 Schedule cleanup cron jobs
- [ ] 14.8 Create feature flag for gradual rollout (optional)

## Dependencies

- Tasks 3.x depend on 1.x (models must exist)
- Tasks 4.x depend on 1.x and 3.x
- Tasks 5.x depend on 1.x, 2.x, 3.x, 4.x
- Tasks 6.x depend on 1.x
- Tasks 7.x depend on 5.x and 6.x
- Tasks 8.x depend on 7.x
- Tasks 9.x depend on 2.x
- Tasks 10.x depend on all implementation tasks
- Tasks 11-14 can proceed in parallel with testing

## Estimated Timeline

- Phase 1 (Models): 2 days
- Phase 2 (File Upload): 1 day
- Phase 3 (Section Management): 1 day
- Phase 4 (Branch Logic): 2 days
- Phase 5 (Forms): 2 days
- Phase 6 (Drafts): 1.5 days
- Phase 7 (Views): 1.5 days
- Phase 8 (Templates): 1 day
- Phase 9 (File Management): 1 day
- Phase 10 (Testing): 2 days
- Phase 11-14 (Docs, Perf, Security, Deploy): 2 days

**Total: ~17 days** (approximately 3-4 weeks with buffer)
