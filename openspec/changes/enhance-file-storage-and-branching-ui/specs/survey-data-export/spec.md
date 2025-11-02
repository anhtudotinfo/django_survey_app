# Spec Delta: Survey Data Export

**Capability**: `survey-data-export` (NEW)  
**Change**: `enhance-file-storage-and-branching-ui`

## ADDED Requirements

### Requirement: CSV Export with File URLs

The system SHALL include accessible file URLs in CSV exports for file upload questions.

#### Scenario: Export survey with file uploads to CSV
- **WHEN** administrator exports survey responses to CSV
- **AND** survey contains file upload questions with uploaded files
- **THEN** CSV includes a "File URL" column for each file upload question
- **AND** URLs are clickable and download the uploaded files
- **AND** URLs work for both local storage and Google Drive files

#### Scenario: Export with missing files
- **WHEN** administrator exports survey with file upload questions
- **AND** some responses have no files uploaded
- **THEN** CSV shows "No file uploaded" for empty file fields
- **AND** export completes successfully without errors

#### Scenario: Export with multiple file types
- **WHEN** survey has both local storage and Google Drive files
- **AND** administrator exports responses
- **THEN** local files generate absolute URLs (e.g., https://domain.com/media/...)
- **AND** Google Drive files use shareable links (e.g., https://drive.google.com/...)
- **AND** all URLs are accessible without authentication

### Requirement: Survey-Specific Export Organization

The system SHALL organize exported files in survey-specific directories with timestamps.

#### Scenario: Export responses with organized structure
- **WHEN** administrator exports survey responses
- **THEN** export file is saved to `exports/{survey_slug}/` directory
- **AND** filename includes timestamp: `{survey_slug}_{YYYY-MM-DD_HH-MM-SS}.csv`
- **AND** directory is created automatically if it doesn't exist

#### Scenario: Multiple exports of same survey
- **WHEN** administrator exports same survey multiple times
- **THEN** each export has unique timestamped filename
- **AND** previous exports are preserved (not overwritten)
- **AND** all exports are accessible in the survey's export directory

### Requirement: Export Options Configuration

The system SHALL allow administrators to configure export options.

#### Scenario: Include file URLs option
- **WHEN** administrator initiates export
- **THEN** checkbox option "Include file download URLs" is available
- **AND** option is checked by default
- **WHEN** option is checked
- **THEN** file URLs are included in CSV export

#### Scenario: Bundle files option (optional)
- **WHEN** administrator initiates export
- **THEN** checkbox option "Bundle uploaded files (ZIP)" is available
- **WHEN** option is checked
- **THEN** export generates ZIP archive containing CSV and uploaded files
- **AND** ZIP archive includes folder structure matching survey structure

## MODIFIED Requirements

None - This is a new capability.

## REMOVED Requirements

None - This is a new capability.
