# Specification: Survey Field Types

## MODIFIED Requirements

### Requirement: Field Type Selection Interface

The system SHALL provide a modal interface for administrators to select from available field types when creating questions, including all supported types.

#### Scenario: Admin opens field type selector
- **WHEN** an administrator clicks "Add Question" in the survey builder
- **THEN** a modal titled "Field Type" appears
- **AND** the modal displays a grid of field type options
- **AND** each field type shows an icon and label
- **AND** the modal includes a close button

#### Scenario: Field types displayed in selector
- **WHEN** the field type selector modal is displayed
- **THEN** the following field types are shown:
  - Text (icon: font/text icon)
  - Number (icon: hashtag/number icon)
  - Radio (icon: radio button icon)
  - Select (icon: dropdown icon)
  - Multi Select (icon: checkboxes icon)
  - Text Area (icon: paragraph icon)
  - URL (icon: link icon)
  - Email (icon: envelope icon)
  - Date (icon: calendar icon)
  - Rating (icon: star icon)
  - **File Upload (icon: cloud upload/file upload icon)**
- **AND** each option is presented as a clickable card
- **AND** hovering over an option highlights it

#### Scenario: Admin selects field type
- **WHEN** an administrator clicks on a field type option
- **THEN** the modal closes
- **AND** the system navigates to the question creation form
- **AND** the form is pre-configured with the selected field type

#### Scenario: Admin closes modal without selection
- **WHEN** an administrator clicks the close button or clicks outside the modal
- **THEN** the modal closes
- **AND** no question creation form is opened
- **AND** the administrator remains on the survey builder page

## ADDED Requirements

### Requirement: File Upload Type Configuration

The system SHALL allow administrators to configure file upload questions with specific restrictions and settings to control what files respondents can upload.

#### Scenario: Configure allowed file types
- **WHEN** an administrator creates a file upload question
- **THEN** the form displays checkboxes for common file types:
  - PDF Documents
  - Word Documents (DOC/DOCX)
  - Images (JPG, PNG, GIF)
  - Excel Spreadsheets (XLS/XLSX)
  - Other (with custom extensions input)
- **AND** multiple file types can be selected simultaneously
- **AND** selecting "Other" reveals a text input for custom extensions

#### Scenario: Set maximum file size
- **WHEN** an administrator configures a file upload question
- **THEN** a max file size control is displayed (range: 1-50 MB)
- **AND** the control shows the current value in megabytes
- **AND** the default value is 5 MB

#### Scenario: Enable multiple file uploads
- **WHEN** an administrator toggles "Allow Multiple Files"
- **THEN** a max files count input appears
- **AND** the max files range is 1-10
- **AND** the default value is 3 files

#### Scenario: View file upload preview
- **WHEN** an administrator configures file upload settings
- **THEN** a preview panel shows how the field will appear to respondents
- **AND** the preview includes the configured accept attribute
- **AND** the preview shows help text describing allowed types and size limit
- **AND** the preview updates in real-time as settings change

### Requirement: File Upload Context Data

The system SHALL provide structured context data for file upload configuration in admin views, ensuring consistent rendering and validation.

#### Scenario: File type data structure
- **WHEN** the question creation form is rendered for file upload type
- **THEN** the context includes file upload configuration data
- **AND** the data includes mappings for file type labels and extensions
- **AND** the data includes default values for max size and file count
- **AND** the data is accessible to JavaScript components for client-side validation
