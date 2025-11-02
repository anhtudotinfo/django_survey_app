# Spec Delta: Survey Branch Logic

**Capability**: `survey-branch-logic`  
**Change**: `enhance-file-storage-and-branching-ui`

## ADDED Requirements

### Requirement: Inline Question Branching Configuration

The system SHALL allow administrators to configure section branching directly in the question creation/editing interface for radio questions.

#### Scenario: Enable branching for radio question
- **WHEN** administrator creates or edits a radio question
- **THEN** "Enable section branching" toggle is visible
- **WHEN** toggle is enabled
- **THEN** branching configuration UI is displayed
- **AND** section selector dropdowns appear for each radio option

#### Scenario: Configure branch targets for each option
- **WHEN** branching is enabled for a question
- **THEN** each radio choice has a section selector dropdown
- **AND** dropdown includes options: "(Continue to next section)", "(End survey)", and all survey sections
- **WHEN** administrator selects target section for an option
- **THEN** selection is saved in question configuration
- **AND** visual preview shows branching flow

#### Scenario: Preview branching flow
- **WHEN** administrator configures branching for question
- **THEN** "Preview Branching Flow" section is available
- **WHEN** section is expanded
- **THEN** visual representation shows: Question → Option A → Section X, Option B → Section Y
- **AND** preview updates dynamically as configuration changes

#### Scenario: Save question with branching
- **WHEN** administrator saves question with branching enabled
- **THEN** enable_branching flag is set to true
- **AND** branch_config JSON stores mapping: {choice_value: section_id}
- **AND** configuration is validated (section IDs must exist in same survey)
- **AND** success message confirms branching is configured

### Requirement: Question-Level Branching Evaluation

The system SHALL evaluate question-level branching during survey navigation with priority over section-level rules.

#### Scenario: Navigate using question branching
- **WHEN** user submits section with question that has branching enabled
- **AND** user selected an option with configured branch target
- **THEN** system navigates to the target section specified in question configuration
- **AND** section-level branch rules are not evaluated (question takes priority)

#### Scenario: End survey from question branching
- **WHEN** user selects option configured to "(End survey)"
- **AND** submits the section
- **THEN** survey ends immediately
- **AND** user sees success page
- **AND** remaining sections are skipped

#### Scenario: Continue to next section by default
- **WHEN** user selects option not configured with branch target
- **OR** branching is not enabled for the question
- **THEN** system continues to next section in sequence
- **OR** evaluates section-level branch rules if they exist

### Requirement: Branching Precedence and Compatibility

The system SHALL maintain backward compatibility with existing section-level branching while giving priority to question-level branching.

#### Scenario: Question branching takes priority
- **WHEN** section has both question-level branching and section-level BranchRule objects
- **THEN** question-level branching is evaluated first
- **WHEN** question branching matches
- **THEN** target section from question config is used
- **AND** section-level rules are not evaluated

#### Scenario: Fall back to section rules
- **WHEN** section has section-level BranchRule objects
- **AND** no questions in section have branching enabled
- **THEN** section-level rules are evaluated as before
- **AND** navigation works exactly as it did previously

#### Scenario: Mixed branching in survey
- **WHEN** survey has some questions with branching and some without
- **AND** some sections have BranchRule objects
- **THEN** each section evaluates question branching first, then section rules
- **AND** branching works correctly for all questions and sections

### Requirement: Branching Configuration Validation

The system SHALL validate branching configuration to prevent invalid navigation flows.

#### Scenario: Validate branch targets exist
- **WHEN** administrator configures branch target for option
- **AND** attempts to save question
- **THEN** system validates that target section ID exists
- **AND** validates that target section belongs to same survey
- **OR** displays error message if validation fails

#### Scenario: Prevent branching for non-radio questions
- **WHEN** administrator tries to enable branching for non-radio question type
- **THEN** system displays error message
- **AND** branching toggle is disabled or hidden
- **AND** question cannot be saved with branching enabled

#### Scenario: Warn about circular branching (optional)
- **WHEN** administrator configures branching that could create loops
- **THEN** system displays warning message
- **AND** administrator can choose to save anyway or modify configuration

## MODIFIED Requirements

None - Existing branching capabilities remain unchanged, this adds a complementary feature.

## REMOVED Requirements

None
