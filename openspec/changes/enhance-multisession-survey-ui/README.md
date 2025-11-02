# Enhanced Multi-Session Survey Builder UI

## Overview

This change proposal enhances the Django survey application's admin interface to provide a modern, intuitive experience for creating and managing complex multi-session surveys.

## Quick Summary

**Problem**: The current survey builder interface lacks visual tools for managing sections, hides the file upload field type option, and provides no drag-and-drop capabilities.

**Solution**: Add modern UI components including:
- File Upload option in the field type selector modal
- Collapsible section manager with drag-and-drop
- Visual question redistribution between sections
- File upload configuration panel with live preview
- REST API endpoints for dynamic operations

## Key Features

### 1. File Upload Field Type Visibility
- Add "File Upload" to the modal when creating questions
- File configuration panel with:
  - Allowed file types (PDF, DOC, Images, Excel, Custom)
  - Max file size selector (1-50 MB)
  - Multiple files toggle
  - Live preview

### 2. Section Management
- Collapsible section cards
- Inline editing (double-click to edit name/description)
- Drag-and-drop section reordering
- Question count badges
- Delete with confirmation

### 3. Question Redistribution
- Drag questions between sections
- Unassigned questions area
- Visual drop zones
- Automatic ordering updates

### 4. Technical Implementation
- Alpine.js for reactive components
- Sortable.js for drag-and-drop
- REST-style API endpoints
- Progressive enhancement (works without JS)
- Mobile responsive

## Files Changed

- `proposal.md` - Problem statement and impact analysis
- `tasks.md` - Detailed implementation checklist (7 phases)
- `design.md` - Technical design and architecture decisions
- `specs/survey-builder/spec.md` - New capability specification
- `specs/survey-field-types/spec.md` - Modified capability specification

## Implementation Phases

1. **Phase 1**: File Upload Field Type in UI (High Priority, Week 1)
2. **Phase 2**: Section Manager UI (High Priority, Week 2)
3. **Phase 3**: Question Redistribution (Medium Priority, Week 3)
4. **Phase 4**: Enhanced Question Creation (Medium Priority, Week 3)
5. **Phase 5**: Visual Flow Builder (Low Priority, Optional)
6. **Phase 6**: Documentation and Polish (High Priority, Week 4)
7. **Phase 7**: Testing and Deployment (High Priority, Week 4-5)

## Dependencies

- Alpine.js (~15KB) - Reactive UI components
- Sortable.js - Drag-and-drop functionality
- TailwindCSS (already in use) - Styling

## Breaking Changes

**None** - All changes are additive and backward compatible.

## Database Changes

**None required** - Uses existing Section, Question, and BranchRule models.

## Validation Status

✅ **Validated with OpenSpec CLI** - All requirements include scenarios, proper structure confirmed.

## Next Steps

1. Review this proposal with stakeholders
2. Get approval to proceed with implementation
3. Begin Phase 1: File Upload Field Type in UI
4. Set up staging environment for testing

## Related Changes

- `add-sections-branching-fileupload` - Backend implementation of sections and file upload (already completed)
- `translate-uzbek-to-english` - UI translation (already completed)

## Questions?

See detailed documentation in:
- `proposal.md` - Why and what
- `design.md` - How and technical decisions
- `tasks.md` - Step-by-step implementation guide
- `specs/` - Formal requirements and scenarios
