# Survey Progress Tracking Capability

## ADDED Requirements

### Requirement: Draft Response Persistence
The system SHALL save survey responses as drafts, allowing users to return and continue completion later.

#### Scenario: Auto-save draft while filling survey
- **WHEN** user completes any section and clicks "Next"
- **THEN** current section answers are saved as draft
- **AND** user can safely close browser
- **AND** progress is preserved

#### Scenario: Manual save draft
- **WHEN** user clicks "Save Draft" button on any section
- **THEN** current section answers are immediately saved
- **AND** user sees confirmation message
- **AND** user can continue editing or leave survey

#### Scenario: Resume draft for authenticated user
- **WHEN** authenticated user returns to survey with existing draft
- **THEN** system detects draft and shows "Continue where you left off" prompt
- **AND** clicking Continue loads saved answers
- **AND** user is taken to last active section

#### Scenario: Resume draft for anonymous user
- **WHEN** anonymous user returns with same session
- **THEN** system detects draft via session key
- **AND** shows resume prompt similar to authenticated users
- **AND** loads saved progress

### Requirement: Draft Data Storage
The system SHALL store draft responses with sufficient metadata for retrieval and cleanup.

#### Scenario: Store draft with metadata
- **WHEN** draft is saved
- **THEN** system records survey ID, user (if authenticated), session key (if anonymous)
- **AND** stores current section position
- **AND** stores answers as JSON structure: {question_id: value}
- **AND** sets expiration timestamp

#### Scenario: Update existing draft
- **WHEN** user with existing draft saves progress again
- **THEN** system updates same draft record (no duplicates)
- **AND** updates current section position
- **AND** merges new answers with existing ones
- **AND** refreshes expiration timestamp

### Requirement: Draft Expiration and Cleanup
The system SHALL automatically remove expired draft responses to prevent database bloat.

#### Scenario: Set draft expiration
- **WHEN** draft is created or updated
- **THEN** expiration is set to 30 days from last update (configurable)
- **AND** expiration timestamp is stored

#### Scenario: Clean expired drafts
- **WHEN** scheduled cleanup job runs
- **THEN** all drafts past expiration are identified
- **AND** expired drafts are deleted from database
- **AND** associated session data is cleared

#### Scenario: Draft conversion to final response
- **WHEN** user submits complete survey
- **THEN** draft is converted to final UserAnswer record
- **AND** draft record is deleted
- **AND** all answers are preserved in Answer records

### Requirement: Draft Security and Privacy
The system SHALL ensure draft responses are accessible only by their owners.

#### Scenario: Authenticated user draft access
- **WHEN** user requests draft
- **THEN** system verifies user ID matches draft owner
- **AND** returns draft only if match
- **AND** returns error if user tries accessing another's draft

#### Scenario: Anonymous user draft access
- **WHEN** anonymous user requests draft
- **THEN** system verifies session key matches draft
- **AND** returns draft only if session matches
- **AND** treats expired sessions as no draft available

#### Scenario: Prevent draft access after survey submission
- **WHEN** user has completed survey
- **THEN** draft is no longer accessible or shown
- **AND** "Resume draft" prompt is not displayed
- **AND** only final responses are visible

### Requirement: Section State Tracking
The system SHALL track which sections have been completed vs in-progress.

#### Scenario: Mark section as completed
- **WHEN** user completes section validation and navigates away
- **THEN** section is marked as completed in draft state
- **AND** progress indicator shows section as done

#### Scenario: Return to completed section
- **WHEN** user navigates back to completed section
- **THEN** all previous answers are pre-filled
- **AND** user can edit answers
- **AND** section remains marked completed unless validation fails

#### Scenario: Resume from last active section
- **WHEN** user resumes draft
- **THEN** system determines last incomplete section
- **AND** presents that section to user first
- **AND** user can navigate back to review completed sections
