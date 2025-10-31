# Survey Branch Logic Capability

## ADDED Requirements

### Requirement: Conditional Section Navigation
The system SHALL support branch rules that direct users to different sections based on their answers.

#### Scenario: Simple equality branch
- **WHEN** user answers "Do you own a car?" with "Yes" in Section 1
- **AND** branch rule exists: if question_id=5 equals "Yes", go to Section 3
- **THEN** clicking "Next" navigates to Section 3 (skipping Section 2)
- **AND** Section 2 is marked as skipped in progress tracking

#### Scenario: Multiple branch rules evaluation
- **WHEN** section has multiple branch rules with different priorities
- **THEN** rules are evaluated in priority order (lowest number first)
- **AND** first matching rule determines next section
- **AND** remaining rules are not evaluated

#### Scenario: No matching branch rule
- **WHEN** user completes section with branch rules
- **AND** no rule conditions match current answers
- **THEN** system defaults to next sequential section
- **AND** navigation behaves as if no branch logic exists

#### Scenario: Branch to survey end
- **WHEN** user answer triggers branch rule with null next_section
- **THEN** survey proceeds directly to final submission
- **AND** all remaining sections are skipped
- **AND** user is shown submission confirmation

### Requirement: Branch Rule Configuration
The system SHALL allow admins to configure branch rules with conditions and targets.

#### Scenario: Create branch rule in admin
- **WHEN** admin edits section in survey admin
- **THEN** branch rules interface is available (inline)
- **AND** admin can add rule specifying: condition question, operator, value, target section
- **AND** rule is validated before saving

#### Scenario: Supported operators
- **WHEN** admin creates branch rule
- **THEN** operator choices include: equals, not_equals, contains, in
- **AND** operator works correctly with question type:
  - equals/not_equals: all field types
  - contains: text fields, multi_select
  - in: compares answer against comma-separated values

#### Scenario: Set rule priority
- **WHEN** admin creates multiple rules for same section
- **THEN** admin assigns priority number to each rule
- **AND** lower numbers evaluate first
- **AND** admin can reorder rules by changing priorities

#### Scenario: Select target section
- **WHEN** admin configures branch rule target
- **THEN** dropdown shows all sections in survey
- **AND** includes "End Survey" option (null value)
- **AND** prevents selecting same section (infinite loop)

### Requirement: Branch Rule Validation
The system SHALL validate branch rules to prevent logical errors and unreachable sections.

#### Scenario: Prevent circular references
- **WHEN** admin saves branch rule that would create cycle (e.g., Section A → B → A)
- **THEN** system detects circular reference
- **AND** shows error message explaining the cycle
- **AND** prevents saving until resolved

#### Scenario: Warn unreachable sections
- **WHEN** admin saves configuration where section becomes unreachable
- **THEN** system shows warning message
- **AND** lists unreachable sections
- **AND** allows save with confirmation (may be intentional)

#### Scenario: Validate condition question exists
- **WHEN** admin creates branch rule
- **THEN** system verifies condition question belongs to current or previous section
- **AND** prevents branching based on questions user hasn't answered yet
- **AND** shows error if invalid question selected

#### Scenario: Validate condition value format
- **WHEN** admin sets condition value
- **THEN** system validates format matches question type:
  - Number fields: value must be numeric
  - Date fields: value must be valid date
  - Select/radio: value must be in choices
- **AND** shows descriptive error if validation fails

### Requirement: Branch Logic User Experience
The system SHALL provide clear feedback when branch logic affects navigation.

#### Scenario: Transparent navigation
- **WHEN** user navigates via branch rule
- **THEN** transition is seamless (no special indication required)
- **AND** progress indicator updates to show current section
- **AND** skipped sections are not counted in progress percentage

#### Scenario: Allow backward navigation through branches
- **WHEN** user clicks "Previous" after branch navigation
- **THEN** system returns to actual previous section visited
- **AND** not necessarily sequential previous section
- **AND** maintains history stack of visited sections

#### Scenario: Re-evaluation on answer change
- **WHEN** user navigates back and changes answer that affects branch
- **AND** navigates forward again
- **THEN** branch rules are re-evaluated with new answer
- **AND** user may follow different path than before
- **AND** previously entered answers in newly visited sections are preserved if exist

### Requirement: Branch Rule Performance
The system SHALL evaluate branch rules efficiently without noticeable delay.

#### Scenario: Fast rule evaluation
- **WHEN** user clicks "Next" on section with up to 10 branch rules
- **THEN** evaluation completes in under 100ms
- **AND** navigation feels instant to user

#### Scenario: Cache branch rule configuration
- **WHEN** system loads survey
- **THEN** all branch rules are loaded and cached
- **AND** subsequent evaluations use cached rules
- **AND** cache is invalidated when admin modifies rules
