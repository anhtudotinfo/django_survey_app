# Specification: Survey Builder

## ADDED Requirements

### Requirement: File Upload Field Type in UI

The system SHALL display the File Upload field type option in the question type selector modal, allowing administrators to create file upload questions through the visual interface.

#### Scenario: Admin views field type options
- **WHEN** an administrator clicks "Add Question" in the survey builder
- **THEN** a modal displays with all available field types including "File Upload"
- **AND** the File Upload option shows an appropriate icon (e.g., upload cloud icon)
- **AND** the File Upload option is visually consistent with other field types

#### Scenario: Admin creates file upload question
- **WHEN** an administrator clicks the "File Upload" option in the modal
- **THEN** the system navigates to the question creation form
- **AND** the form is pre-configured with type_field=10 (File Upload type)
- **AND** the form includes file-specific configuration options

#### Scenario: File configuration panel display
- **WHEN** an administrator creates or edits a file upload question
- **THEN** the form displays a File Upload Settings panel
- **AND** the panel includes checkboxes for allowed file types (PDF, DOC, Images, Excel, Custom)
- **AND** the panel includes a max file size slider (1-50 MB)
- **AND** the panel includes a toggle for allowing multiple files
- **AND** the panel includes a max files input (shown only if multiple files allowed)

#### Scenario: File upload live preview
- **WHEN** an administrator configures file upload settings
- **THEN** a live preview section shows how the upload field will appear to respondents
- **AND** the preview updates immediately when any setting changes
- **AND** the preview displays the accepted file types
- **AND** the preview displays the file size limit

### Requirement: Collapsible Section Manager

The system SHALL provide a collapsible section list interface that allows administrators to view, organize, and manage survey sections visually.

#### Scenario: View section list
- **WHEN** an administrator opens the survey builder
- **THEN** all sections are displayed as collapsible cards
- **AND** each section card shows the section name
- **AND** each section card shows a question count badge
- **AND** each section card has an expand/collapse toggle icon

#### Scenario: Expand section to view questions
- **WHEN** an administrator clicks on a collapsed section
- **THEN** the section expands to reveal its questions
- **AND** questions are displayed as a list within the section
- **AND** each question shows its label and field type

#### Scenario: Collapse section to hide questions
- **WHEN** an administrator clicks on an expanded section
- **THEN** the section collapses to hide its questions
- **AND** the section remains visible as a card with summary information

#### Scenario: View unassigned questions
- **WHEN** the survey has questions without an assigned section
- **THEN** an "Unassigned Questions" area displays below all sections
- **AND** the area is visually distinct (e.g., yellow background)
- **AND** the area shows a count badge of unassigned questions
- **AND** the area displays all questions that have section=null

### Requirement: Inline Section Editing

The system SHALL allow administrators to edit section properties directly within the section manager interface without navigating to separate pages.

#### Scenario: Edit section name inline
- **WHEN** an administrator double-clicks a section name
- **THEN** the section name becomes an editable text input
- **AND** the administrator can type a new name
- **AND** pressing Enter or clicking outside saves the change
- **AND** pressing Escape cancels the edit

#### Scenario: Edit section description inline
- **WHEN** an administrator is editing a section
- **THEN** a description textarea appears below the name input
- **AND** the administrator can enter or modify the description
- **AND** the description saves along with the name

#### Scenario: Save section changes
- **WHEN** an administrator finishes editing a section
- **THEN** the system sends an API request to save changes
- **AND** the UI updates to show the new values
- **AND** a success indicator briefly appears (optional)
- **AND** if save fails, the original values are restored and an error message displays

### Requirement: Section Drag-and-Drop Reordering

The system SHALL enable administrators to reorder sections using drag-and-drop interactions, updating the section sequence accordingly.

#### Scenario: Drag section to new position
- **WHEN** an administrator clicks and holds a section's drag handle
- **THEN** the section becomes draggable
- **AND** a visual indicator shows the section is being dragged (e.g., opacity change)
- **AND** other sections shift to show potential drop positions

#### Scenario: Drop section in new position
- **WHEN** an administrator releases the mouse button while dragging
- **THEN** the section is placed in the new position
- **AND** the system updates section ordering values
- **AND** the ordering is saved to the database via API

#### Scenario: Visual feedback during drag
- **WHEN** a section is being dragged
- **THEN** the dragged section has reduced opacity
- **AND** a drop zone indicator appears between sections
- **AND** the cursor changes to indicate dragging is active

### Requirement: Question Redistribution Between Sections

The system SHALL allow administrators to move questions between sections using drag-and-drop, enabling flexible question organization.

#### Scenario: Drag question to different section
- **WHEN** an administrator clicks and holds a question's drag handle
- **THEN** the question becomes draggable
- **AND** all section question lists become drop zones
- **AND** the unassigned questions area becomes a drop zone

#### Scenario: Drop question in target section
- **WHEN** an administrator drops a question in a different section
- **THEN** the question moves to the target section
- **AND** the question's section field is updated in the database
- **AND** the question's ordering is recalculated within the target section
- **AND** both source and target section question counts update

#### Scenario: Move question to unassigned area
- **WHEN** an administrator drops a question in the unassigned area
- **THEN** the question's section field is set to null
- **AND** the question appears in the unassigned questions list
- **AND** the source section's question count decreases

#### Scenario: Reorder questions within section
- **WHEN** an administrator drags a question to a different position within the same section
- **THEN** the question's ordering value is updated
- **AND** other questions in the section are reordered accordingly
- **AND** the changes are saved to the database

### Requirement: Add Section Operation

The system SHALL provide a button to create new sections, allowing administrators to expand survey structure on demand.

#### Scenario: Create new section
- **WHEN** an administrator clicks the "Add Section" button
- **THEN** a new section is created with default values (name: "New Section", ordering: next available)
- **AND** the new section appears at the end of the section list
- **AND** the new section is automatically expanded
- **AND** the section is saved to the database immediately

### Requirement: Delete Section Operation

The system SHALL allow administrators to delete sections, with questions from deleted sections becoming unassigned rather than being deleted.

#### Scenario: Delete section with confirmation
- **WHEN** an administrator clicks the delete icon on a section
- **THEN** a confirmation dialog appears
- **AND** the dialog warns that questions will become unassigned
- **AND** confirming the deletion removes the section from the database
- **AND** all questions from that section are moved to unassigned

#### Scenario: Cancel section deletion
- **WHEN** an administrator cancels the deletion confirmation
- **THEN** no changes are made
- **AND** the section remains in the list

### Requirement: Question Operations from Section Manager

The system SHALL provide quick access to question editing and deletion directly from the section manager interface.

#### Scenario: Edit question from section view
- **WHEN** an administrator clicks the edit icon on a question
- **THEN** the system navigates to the question edit page
- **AND** the page is pre-populated with the question's current values

#### Scenario: Delete question from section view
- **WHEN** an administrator clicks the delete icon on a question
- **THEN** a confirmation dialog appears
- **AND** confirming the deletion removes the question from the database
- **AND** the section's question count decreases
- **AND** remaining questions are reordered

### Requirement: API Endpoints for Section Management

The system SHALL provide REST-style API endpoints for all section and question management operations, enabling the dynamic UI functionality.

#### Scenario: Fetch survey sections data
- **WHEN** the survey builder loads
- **THEN** a GET request to `/api/survey/{slug}/sections/` returns all sections
- **AND** the response includes section properties (id, name, description, ordering)
- **AND** the response includes nested question data for each section
- **AND** the response includes unassigned questions
- **AND** only authenticated staff users can access this endpoint

#### Scenario: Create section via API
- **WHEN** a POST request is made to `/api/section/create/`
- **THEN** a new section is created in the database
- **AND** the response includes the new section's data
- **AND** the request requires CSRF token for security
- **AND** only authenticated staff users can create sections

#### Scenario: Update section via API
- **WHEN** a PATCH request is made to `/api/section/{id}/update/`
- **THEN** the specified section's properties are updated
- **AND** the response confirms success or reports errors
- **AND** only modified fields are updated

#### Scenario: Delete section via API
- **WHEN** a DELETE request is made to `/api/section/{id}/delete/`
- **THEN** the section is removed from the database
- **AND** associated questions have their section field set to null
- **AND** the response confirms success

#### Scenario: Reorder sections via API
- **WHEN** a POST request is made to `/api/sections/reorder/`
- **THEN** multiple sections' ordering values are updated in bulk
- **AND** the request body contains an array of section IDs with new orderings
- **AND** all updates occur in a single database transaction

#### Scenario: Move question via API
- **WHEN** a POST request is made to `/api/question/{id}/move/`
- **THEN** the question's section and ordering are updated
- **AND** if section_id is null, the question becomes unassigned
- **AND** other questions in the target section are reordered as needed

### Requirement: Progressive Enhancement and Fallback

The system SHALL ensure that basic survey builder functionality remains accessible even if JavaScript is disabled or fails to load.

#### Scenario: JavaScript disabled fallback
- **WHEN** JavaScript is disabled in the browser
- **THEN** the page displays sections and questions in a basic list format
- **AND** traditional links and forms allow editing sections and questions
- **AND** drag-and-drop is not available but up/down ordering buttons work

#### Scenario: API error handling
- **WHEN** an API request fails due to network error
- **THEN** the UI displays an error message
- **AND** the UI reverts to the previous state (rollback)
- **AND** the administrator can retry the operation

### Requirement: Accessibility Compliance

The system SHALL implement accessibility features to ensure the survey builder is usable by administrators with disabilities.

#### Scenario: Keyboard navigation
- **WHEN** an administrator uses only the keyboard
- **THEN** all interactive elements are reachable via Tab key
- **AND** Enter/Space keys activate buttons and toggles
- **AND** Escape key closes modals and cancels edits
- **AND** arrow keys can navigate between sections and questions (optional enhancement)

#### Scenario: Screen reader support
- **WHEN** a screen reader user navigates the survey builder
- **THEN** all sections have descriptive ARIA labels
- **AND** all buttons have meaningful accessible names
- **AND** drag handles announce their purpose
- **AND** state changes (expand/collapse) are announced

#### Scenario: Visual focus indicators
- **WHEN** an administrator navigates using keyboard
- **THEN** focused elements have a visible outline or highlight
- **AND** focus order follows logical reading sequence
- **AND** focus is not lost during dynamic updates

### Requirement: Mobile Responsiveness

The system SHALL adapt the survey builder interface for smaller screens, providing alternative interactions where drag-and-drop is impractical.

#### Scenario: Mobile layout adaptation
- **WHEN** the survey builder is viewed on a mobile device (< 768px width)
- **THEN** sections and questions stack vertically
- **AND** drag handles are hidden
- **AND** up/down arrow buttons appear for reordering
- **AND** edit/delete buttons remain accessible

#### Scenario: Tablet layout adaptation
- **WHEN** the survey builder is viewed on a tablet (768px - 1023px width)
- **THEN** sections display in a single column
- **AND** drag-and-drop remains functional
- **AND** touch interactions are supported

### Requirement: Performance Optimization for Large Surveys

The system SHALL implement performance optimizations to handle surveys with many sections and questions without degrading user experience.

#### Scenario: Lazy loading of section content
- **WHEN** a survey has more than 10 sections
- **THEN** questions are only loaded when a section is expanded
- **AND** collapsing a section optionally unloads its question data

#### Scenario: Debounced autosave
- **WHEN** an administrator makes multiple rapid changes
- **THEN** save operations are debounced to avoid excessive API calls
- **AND** changes are batched where possible
- **AND** a "saving..." indicator shows when saves are pending

#### Scenario: Optimistic UI updates
- **WHEN** an administrator performs an operation (drag, edit, delete)
- **THEN** the UI updates immediately (optimistically)
- **AND** if the API request fails, the UI reverts with an error message
- **AND** the user can retry the failed operation
