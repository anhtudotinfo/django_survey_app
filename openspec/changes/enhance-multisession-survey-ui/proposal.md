# Proposal: Enhanced Multi-Session Survey Builder UI

**Change ID**: `enhance-multisession-survey-ui`  
**Status**: Proposal  
**Created**: 2025-10-31

## Why

The current survey builder interface has limitations that make it difficult for administrators to create and manage complex multi-session surveys:

1. **No visual representation of survey structure**: Admins cannot see sections and their relationships at a glance
2. **Hidden file upload option**: The file upload field type exists in the backend but is not visible in the UI template's field type selector modal
3. **Limited section management**: No drag-and-drop reordering or visual organization of sections
4. **Poor navigation flow visibility**: Branch logic and conditional navigation are configured separately without visual feedback
5. **Cumbersome question organization**: Questions cannot be easily moved between sections

These limitations increase the time and complexity required to build sophisticated multi-session surveys, leading to configuration errors and poor user experience.

## What Changes

This proposal enhances the survey builder UI with modern, intuitive interfaces for creating and managing multi-session surveys:

1. **Add File Upload to Field Type Selector**
   - Display "File Upload" option in the modal that appears when adding questions
   - Update `modal_choice_field_type.html` to include file upload type with appropriate icon
   - Ensure the file upload option links to the correct question creation view

2. **Collapsible Section Manager**
   - Visual section list with expand/collapse functionality
   - Inline section editing (name, description)
   - Question count badges per section
   - Drag-and-drop section reordering
   - Unassigned questions area for questions without sections

3. **Question Redistribution Interface**
   - Drag-and-drop questions between sections
   - Move questions to/from unassigned area
   - Visual drop zones with hover feedback
   - Bulk question operations (move multiple questions)

4. **Enhanced Question Creation Modal**
   - File upload configuration panel with:
     - Allowed file types selector (PDF, DOC, Images, Excel, Custom)
     - Max file size input (MB)
     - Multiple files toggle
     - Live preview of upload field
   - Context-aware section assignment

5. **Visual Flow Builder (Optional Phase 2)**
   - Interactive flowchart showing section sequence
   - Visual branch connections with conditions
   - Circular reference detection and warnings
   - Click nodes to edit sections

## Impact

**Affected Specs**:
- `survey-builder` (new): Admin interface for creating/editing surveys
- `survey-field-types` (modified): Add file upload to UI selector

**Affected Code**:
- `djf_surveys/templates/djf_surveys/components/modal_choice_field_type.html` - Add file upload option
- `djf_surveys/admins/views.py` - Add context for file upload configuration
- `djf_surveys/templates/djf_surveys/admins/form_preview.html` - Enhanced section management UI
- New JavaScript files for drag-and-drop and dynamic interactions
- New CSS for modern UI components

**Breaking Changes**: None - all changes are additive and backward compatible

**Database Changes**: None required - leverages existing Section, Question, and BranchRule models

**User Impact**:
- Administrators: Significantly improved survey building experience
- Survey respondents: No changes
- Existing surveys: Continue to work without modification

**Dependencies**:
- Alpine.js (for reactive components) or vanilla JavaScript
- Sortable.js (for drag-and-drop functionality)
- TailwindCSS (already in use for styling)

**Migration Path**:
- No data migration required
- UI changes can be rolled out incrementally
- Feature flag option for gradual rollout: `ENHANCED_SURVEY_BUILDER_UI`

**Testing Requirements**:
- Unit tests for new view context methods
- Integration tests for drag-and-drop interactions
- Browser compatibility testing (Chrome, Firefox, Safari, Edge)
- Accessibility testing for keyboard navigation
- Mobile responsiveness testing
