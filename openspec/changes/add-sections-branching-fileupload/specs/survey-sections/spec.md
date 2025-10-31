# Survey Sections Capability

## ADDED Requirements

### Requirement: Section Organization
The system SHALL allow surveys to be organized into multiple named sections, each containing one or more questions.

#### Scenario: Create section in survey
- **WHEN** admin creates a section with name "Personal Information" and ordering 1
- **THEN** the section is saved and associated with the survey
- **AND** questions can be assigned to this section

#### Scenario: Order sections sequentially
- **WHEN** admin creates sections with ordering values 1, 2, 3
- **THEN** users navigate through sections in that order during survey completion
- **AND** progress indicator reflects section sequence

#### Scenario: Display section information
- **WHEN** user views a section
- **THEN** section name is displayed as heading
- **AND** section description (if provided) is shown below the name
- **AND** only questions belonging to that section are visible

### Requirement: Default Section for Backward Compatibility
The system SHALL automatically create a default section for existing surveys without sections.

#### Scenario: Migrate existing survey
- **WHEN** system runs migration for surveys created before sections feature
- **THEN** a default section named "Main" is created for each survey
- **AND** all existing questions are assigned to this default section
- **AND** survey behavior remains unchanged for users

#### Scenario: New survey without sections
- **WHEN** admin creates new survey without explicitly defining sections
- **THEN** a default section is automatically created
- **AND** all questions are added to default section
- **AND** survey appears as single-page form (backward compatible behavior)

### Requirement: Section Navigation
The system SHALL provide navigation controls to move between sections during survey completion.

#### Scenario: Navigate to next section
- **WHEN** user completes current section and clicks "Next"
- **THEN** current section answers are validated
- **AND** if valid, user is shown next section in sequence
- **AND** if invalid, errors are displayed without navigation

#### Scenario: Navigate to previous section
- **WHEN** user clicks "Previous" button on non-first section
- **THEN** user returns to previous section
- **AND** previously entered answers are pre-filled
- **AND** no validation is performed on current section

#### Scenario: First section navigation
- **WHEN** user is on first section
- **THEN** "Previous" button is hidden or disabled
- **AND** only "Next" button is available

#### Scenario: Last section submission
- **WHEN** user is on last section
- **THEN** "Next" button is replaced with "Submit" button
- **AND** clicking Submit validates final section and saves complete response

### Requirement: Progress Tracking Display
The system SHALL display visual progress indicator showing survey completion status across sections.

#### Scenario: Show progress percentage
- **WHEN** user views any section
- **THEN** progress bar shows percentage: (current section / total sections) * 100
- **AND** text indicator shows "Section X of Y"

#### Scenario: Update progress on navigation
- **WHEN** user navigates to different section
- **THEN** progress indicator updates immediately
- **AND** completed sections are visually marked (e.g., different color)

### Requirement: Section Management in Admin
The system SHALL provide admin interface for managing sections within surveys.

#### Scenario: Add section via admin
- **WHEN** admin accesses survey edit page
- **THEN** section management interface is available
- **AND** admin can add new section with name, description, and ordering

#### Scenario: Reorder sections
- **WHEN** admin changes ordering values of sections
- **THEN** sections are reordered accordingly in user flow
- **AND** existing user responses are not affected

#### Scenario: Delete section with questions
- **WHEN** admin attempts to delete section containing questions
- **THEN** system shows warning about questions being orphaned
- **AND** admin must reassign questions or confirm deletion
- **AND** deletion is prevented if it would leave questions without section

#### Scenario: Assign questions to sections
- **WHEN** admin edits question
- **THEN** dropdown shows all sections in parent survey
- **AND** admin can select section for question
- **AND** question appears in selected section during survey
