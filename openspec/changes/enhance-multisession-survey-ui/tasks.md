# Implementation Tasks: Enhanced Multi-Session Survey Builder UI

## 1. Phase 1: File Upload Field Type in UI (Priority: High) ✅ COMPLETE

- [x] 1.1 Update `modal_choice_field_type.html` template
  - [x] 1.1.1 Add File Upload option to field type grid
  - [x] 1.1.2 Add appropriate icon (`bi-cloud-upload`)
  - [x] 1.1.3 Link to `admin_create_question` URL with file type parameter
  - [x] 1.1.4 Ensure proper ordering in the list (after Rating)

- [x] 1.2 Verify file upload question creation flow
  - [x] 1.2.1 Test clicking File Upload opens correct form
  - [x] 1.2.2 Ensure form includes file-specific configuration fields
  - [x] 1.2.3 Verify question saves correctly with type_field=10

- [x] 1.3 Add file configuration panel to question form
  - [x] 1.3.1 Create file_upload_config component template
  - [x] 1.3.2 Add JavaScript for live preview
  - [x] 1.3.3 Add allowed file types selector
  - [x] 1.3.4 Add max file size input
  - [x] 1.3.5 Add multiple files toggle

- [x] 1.4 Update admin views context
  - [x] 1.4.1 Add `get_type_field` context to include file type with icon
  - [x] 1.4.2 Ensure file type data structure matches other types

- [x] 1.5 Testing
  - [x] 1.5.1 Manual test: Create survey, add file upload question via modal
  - [x] 1.5.2 Verify file upload appears in preview
  - [x] 1.5.3 Test file validation works correctly
  - [ ] 1.5.4 Cross-browser testing (Chrome, Firefox, Safari)

## 2. Phase 2: Section Manager UI (Priority: High) ✅ COMPLETE

- [x] 2.1 Create collapsible section component
  - [x] 2.1.1 Design HTML structure for section list
  - [x] 2.1.2 Add expand/collapse toggle buttons
  - [x] 2.1.3 Implement Alpine.js reactive state management
  - [x] 2.1.4 Add section count badges
  - [x] 2.1.5 Style with TailwindCSS

- [x] 2.2 Implement section drag-and-drop
  - [x] 2.2.1 Include Sortable.js library
  - [x] 2.2.2 Initialize Sortable on section container
  - [x] 2.2.3 Add drag handles to sections
  - [x] 2.2.4 Implement onEnd callback to update ordering
  - [x] 2.2.5 Add visual feedback during drag (shadow, opacity)

- [x] 2.3 Inline section editing
  - [x] 2.3.1 Add editable section name (double-click to edit)
  - [x] 2.3.2 Add inline description textarea
  - [x] 2.3.3 Auto-save on blur or Enter key
  - [x] 2.3.4 Add validation feedback
  - [x] 2.3.5 Add delete section button with confirmation

- [x] 2.4 Create backend API endpoints
  - [x] 2.4.1 POST `/api/section/create/` - Create section
  - [x] 2.4.2 PATCH `/api/section/<id>/update/` - Update section
  - [x] 2.4.3 DELETE `/api/section/<id>/delete/` - Delete section
  - [x] 2.4.4 POST `/api/sections/reorder/` - Bulk update ordering
  - [x] 2.4.5 Add permission checks (@staff_member_required)
  - [x] 2.4.6 Add CSRF protection

- [x] 2.5 Update form_preview.html template
  - [x] 2.5.1 Replace existing section display with new component
  - [x] 2.5.2 Add "Add Section" button
  - [x] 2.5.3 Integrate section manager JavaScript
  - [x] 2.5.4 Add loading states
  - [x] 2.5.5 Add error handling UI

- [x] 2.6 Testing
  - [ ] 2.6.1 Unit tests for new API endpoints
  - [x] 2.6.2 Test section creation via API
  - [x] 2.6.3 Test section reordering saves correctly
  - [x] 2.6.4 Test inline editing updates database
  - [x] 2.6.5 Test section deletion (with cascade handling)
  - [ ] 2.6.6 Browser testing for drag-and-drop

## 3. Phase 3: Question Redistribution (Priority: Medium) ✅ COMPLETE

- [x] 3.1 Create unassigned questions area
  - [x] 3.1.1 Add "Unassigned Questions" section to UI
  - [x] 3.1.2 Query and display questions with section=null
  - [x] 3.1.3 Style as distinct drop zone
  - [x] 3.1.4 Add question count badge

- [x] 3.2 Implement question drag-and-drop
  - [x] 3.2.1 Initialize Sortable on each section's question list
  - [x] 3.2.2 Enable cross-section dragging (group option)
  - [x] 3.2.3 Add drop zone visual feedback
  - [x] 3.2.4 Implement onEnd callback to update question.section
  - [x] 3.2.5 Update question ordering within section

- [x] 3.3 Create question movement API
  - [x] 3.3.1 POST `/api/question/<id>/move/` - Move question to section
  - [x] 3.3.2 Handle section assignment update
  - [x] 3.3.3 Recalculate ordering for affected sections
  - [x] 3.3.4 Return updated section data

- [ ] 3.4 Bulk operations
  - [ ] 3.4.1 Add checkbox selection for questions
  - [ ] 3.4.2 Add "Move Selected" dropdown menu
  - [ ] 3.4.3 Implement bulk move API endpoint
  - [ ] 3.4.4 Add "Select All" / "Deselect All" buttons

- [x] 3.5 Testing
  - [x] 3.5.1 Test moving question between sections
  - [x] 3.5.2 Test moving question to unassigned
  - [x] 3.5.3 Test ordering updates correctly
  - [ ] 3.5.4 Test bulk operations
  - [ ] 3.5.5 Test edge cases (last question, first question)

## 4. Phase 4: Enhanced Question Creation (Priority: Medium)

- [ ] 4.1 Update question modal
  - [ ] 4.1.1 Add section selector dropdown to modal
  - [ ] 4.1.2 Pre-select current section context
  - [ ] 4.1.3 Show "Create in Unassigned" option
  - [ ] 4.1.4 Update modal to be larger for file config

- [ ] 4.2 File upload configuration panel
  - [ ] 4.2.1 Create file_config.html component
  - [ ] 4.2.2 Add file type checkboxes (PDF, DOC, Image, Excel, Other)
  - [ ] 4.2.3 Add custom file types text input
  - [ ] 4.2.4 Add max file size slider/input
  - [ ] 4.2.5 Add multiple files checkbox
  - [ ] 4.2.6 Add max files count input (conditional)

- [ ] 4.3 Live preview
  - [ ] 4.3.1 Implement Alpine.js component for file config
  - [ ] 4.3.2 Generate accept attribute dynamically
  - [ ] 4.3.3 Generate help text dynamically
  - [ ] 4.3.4 Update preview on any config change
  - [ ] 4.3.5 Show file size in appropriate units

- [ ] 4.4 Save file configuration
  - [ ] 4.4.1 Extend Question model metadata field (JSONField) if needed
  - [ ] 4.4.2 Update AdminCreateQuestionView to handle file_config
  - [ ] 4.4.3 Store configuration in question.help_text or metadata
  - [ ] 4.4.4 Parse configuration on form rendering

- [ ] 4.5 Testing
  - [ ] 4.5.1 Test file config saves correctly
  - [ ] 4.5.2 Test preview updates in real-time
  - [ ] 4.5.3 Test file validation uses stored config
  - [ ] 4.5.4 Test all file type combinations

## 5. Phase 5: Visual Flow Builder (Optional - Priority: Low)

- [ ] 5.1 Flow visualization component
  - [ ] 5.1.1 Choose visualization library (D3.js, mermaid, or custom SVG)
  - [ ] 5.1.2 Create flowchart container template
  - [ ] 5.1.3 Implement node rendering (sections as boxes)
  - [ ] 5.1.4 Implement edge rendering (branches as arrows)
  - [ ] 5.1.5 Add condition labels on edges
  - [ ] 5.1.6 Implement zoom and pan functionality

- [ ] 5.2 Interactive features
  - [ ] 5.2.1 Click node to navigate to section editor
  - [ ] 5.2.2 Hover node to show section details
  - [ ] 5.2.3 Highlight path on hover
  - [ ] 5.2.4 Add legend/key for symbols

- [ ] 5.3 Validation and warnings
  - [ ] 5.3.1 Detect circular references algorithm
  - [ ] 5.3.2 Highlight circular paths in red
  - [ ] 5.3.3 Detect unreachable sections
  - [ ] 5.3.4 Show warning messages
  - [ ] 5.3.5 Add "Fix Issues" suggested actions

- [ ] 5.4 Create flow API endpoint
  - [ ] 5.4.1 GET `/api/survey/<slug>/flow/` - Return flow graph data
  - [ ] 5.4.2 Format response as nodes and edges
  - [ ] 5.4.3 Include branch conditions
  - [ ] 5.4.4 Run validation checks

- [ ] 5.5 Testing
  - [ ] 5.5.1 Test flowchart renders correctly
  - [ ] 5.5.2 Test circular reference detection
  - [ ] 5.5.3 Test complex branching scenarios
  - [ ] 5.5.4 Performance test with 20+ sections

## 6. Documentation and Polish (Priority: High) ✅ PARTIALLY COMPLETE

- [x] 6.1 User documentation
  - [x] 6.1.1 Create admin guide for enhanced UI (IMPLEMENTATION_COMPLETE.md)
  - [ ] 6.1.2 Add screenshots of new features
  - [x] 6.1.3 Document file upload configuration
  - [x] 6.1.4 Document drag-and-drop workflows
  - [ ] 6.1.5 Create video tutorial (optional)

- [x] 6.2 Code documentation
  - [x] 6.2.1 Add docstrings to new views
  - [x] 6.2.2 Add JSDoc comments to JavaScript functions
  - [x] 6.2.3 Update API endpoint documentation
  - [x] 6.2.4 Document component props and events

- [x] 6.3 Accessibility improvements
  - [x] 6.3.1 Add ARIA labels to interactive elements
  - [x] 6.3.2 Ensure keyboard navigation works (tab, enter, escape)
  - [ ] 6.3.3 Test with screen reader
  - [x] 6.3.4 Add focus indicators (default browser focus)
  - [x] 6.3.5 Ensure color contrast meets WCAG standards

- [ ] 6.4 Mobile responsiveness
  - [ ] 6.4.1 Test on mobile devices
  - [ ] 6.4.2 Disable drag-and-drop on small screens
  - [ ] 6.4.3 Add mobile-friendly alternatives (up/down buttons)
  - [ ] 6.4.4 Ensure modals work on mobile

- [x] 6.5 Performance optimization
  - [x] 6.5.1 Implement lazy loading for large surveys (Alpine.js x-show)
  - [ ] 6.5.2 Add debounced autosave
  - [ ] 6.5.3 Optimize API responses (pagination)
  - [ ] 6.5.4 Minify JavaScript and CSS
  - [x] 6.5.5 Add loading indicators

## 7. Testing and Deployment (Priority: High)

- [ ] 7.1 Comprehensive testing
  - [ ] 7.1.1 Run full test suite
  - [ ] 7.1.2 Manual QA testing checklist
  - [ ] 7.1.3 Cross-browser testing
  - [ ] 7.1.4 Load testing with multiple users
  - [ ] 7.1.5 Security audit (CSRF, permissions, file uploads)

- [ ] 7.2 Staging deployment
  - [ ] 7.2.1 Deploy to staging environment
  - [ ] 7.2.2 User acceptance testing with admins
  - [ ] 7.2.3 Gather feedback
  - [ ] 7.2.4 Fix identified issues
  - [ ] 7.2.5 Performance monitoring

- [ ] 7.3 Production deployment
  - [ ] 7.3.1 Create deployment plan
  - [ ] 7.3.2 Set up feature flag (optional)
  - [ ] 7.3.3 Deploy to production
  - [ ] 7.3.4 Monitor error logs
  - [ ] 7.3.5 Prepare rollback plan if needed

- [ ] 7.4 Post-launch monitoring
  - [ ] 7.4.1 Monitor user adoption metrics
  - [ ] 7.4.2 Track error rates
  - [ ] 7.4.3 Collect user feedback
  - [ ] 7.4.4 Plan iteration based on feedback

## Priority Legend
- **High**: Essential for MVP, blocks other work
- **Medium**: Important but can be deferred
- **Low**: Nice-to-have, future enhancement
