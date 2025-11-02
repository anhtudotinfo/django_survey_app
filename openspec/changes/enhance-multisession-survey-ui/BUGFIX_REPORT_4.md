# Bug Fix Report #4: Section State Preservation and Drag-and-Drop

**Date**: 2025-10-31  
**Bug ID**: Sections collapse after drag, cannot drag sections properly  
**Severity**: Critical (Core functionality unusable)  
**Status**: ✅ FIXED

## Problem Description

### User Report
> "lỗi trên vẫn chưa khắc phục: tôi vấn chưa thay đổi được vị trí session và khi click vào session thì nó không mở và đóng lại rất nhanh tôi nghĩ lỗi phần script"

Translation: "The bug still not fixed: I still cannot change section position and when I click on section it doesn't open and closes very quickly. I think the error is in the script"

### Root Causes

#### Issue 1: Section State Not Preserved
Every time `loadData()` was called, it reset all sections to `expanded: false`:

```javascript
// BEFORE (Broken)
async loadData() {
    const data = await fetch(...).json();
    this.sections = data.sections.map(s => ({
        ...s, 
        expanded: false,  // ❌ Always reset to false!
        editing: false
    }));
}
```

**When loadData() was called**:
- After moving questions → Section collapsed
- After deleting questions → Section collapsed
- After reordering sections → Section collapsed
- User experience: Sections flash open/closed

#### Issue 2: Sortable Not Properly Configured
Sortable.js wasn't configured with proper selectors and handles:
- Missing `draggable` selector for sections
- Missing `handle` selector for questions
- Sortable initialized even for collapsed sections (performance issue)
- No filters configured

#### Issue 3: Sortable Not Reinitialized After Toggle
When expanding a section, Sortable.js wasn't reinitialized for that section's questions, so drag-and-drop didn't work.

## Solution

### Fix 1: Preserve Section State

Added state preservation mechanism to `loadData()`:

```javascript
// AFTER (Fixed)
async loadData(preserveState = false) {
    const data = await fetch(...).json();
    
    // Save current state
    const stateMap = new Map();
    if (preserveState) {
        this.sections.forEach(s => {
            stateMap.set(s.id, {
                expanded: s.expanded,  // ✅ Remember if section was open
                editing: s.editing
            });
        });
    }
    
    // Restore state when rebuilding
    this.sections = data.sections.map(s => {
        const savedState = stateMap.get(s.id);
        return {
            ...s, 
            expanded: savedState ? savedState.expanded : false,  // ✅ Restore!
            editing: savedState ? savedState.editing : false,
        };
    });
}
```

**Usage**:
```javascript
// When state should be preserved
await this.loadData(true);  // Keep sections open/closed as they were

// When state should reset (e.g., initial load)
await this.loadData();  // All sections start collapsed
```

### Fix 2: Configure Sortable.js Properly

**For Sections**:
```javascript
new Sortable(sectionsContainer, {
    handle: '.drag-handle',           // ✅ Only drag by handle
    draggable: '.section-card',       // ✅ What can be dragged
    filter: '.filtered',              // ✅ What to ignore
    animation: 150,
    ghostClass: 'opacity-50',
    dragClass: 'shadow-2xl',
    onEnd: (evt) => {
        this.reorderSections(evt.oldIndex, evt.newIndex);
    }
});
```

**For Questions**:
```javascript
this.sections.forEach(section => {
    if (listEl && section.expanded) {  // ✅ Only init if section is open
        new Sortable(listEl, {
            group: 'questions',
            draggable: '.question-item',      // ✅ What can be dragged
            handle: '.bi-grip-vertical',      // ✅ Drag by grip icon
            animation: 150,
            onEnd: (evt) => {
                this.moveQuestion(...);
            }
        });
    }
});
```

### Fix 3: Reinitialize Sortable on Toggle

```javascript
toggleSection(sectionId) {
    const section = this.sections.find(s => s.id === sectionId);
    if (section && !section.editing) {
        section.expanded = !section.expanded;
        
        // ✅ Reinitialize sortable after DOM updates
        this.$nextTick(() => {
            if (section.expanded) {
                this.initSortable();  // Make questions draggable
            }
        });
    }
}
```

### Fix 4: Don't Reload After Reorder

```javascript
async reorderSections(oldIndex, newIndex) {
    // Move in array
    const section = this.sections[oldIndex];
    this.sections.splice(oldIndex, 1);
    this.sections.splice(newIndex, 0, section);
    
    // Save to server
    await fetch('/api/sections/reorder/', {
        method: 'POST',
        body: JSON.stringify({
            sections: this.sections.map((s, idx) => ({id: s.id, ordering: idx}))
        })
    });
    
    // ✅ Don't call loadData() - state is already correct!
}
```

## Changes Summary

### Files Modified
- `djf_surveys/templates/djf_surveys/components/section_manager.html`

### Lines Changed
1. `loadData()` - Added `preserveState` parameter and state preservation logic (20 lines)
2. `reorderSections()` - Removed unnecessary `loadData()` call (1 line removed)
3. `deleteSection()` - Changed to `loadData(true)` (1 line)
4. `moveQuestion()` - Changed to `loadData(true)` (2 lines)
5. `deleteQuestion()` - Changed to `loadData(true)` (1 line)
6. `initSortable()` - Added proper selectors and handles (5 lines)
7. `toggleSection()` - Added sortable reinitialization (6 lines)

## Verification

### Test Checklist

**Section Expand/Collapse**:
- [x] Click section → Opens
- [x] Click again → Closes
- [x] Stays open after dragging questions
- [x] Stays open after deleting questions
- [x] Stays closed after reordering sections

**Section Drag-and-Drop**:
- [x] Drag section by ⋮ handle → Moves
- [x] Cannot drag by clicking other areas
- [x] Section order persists
- [x] Sections don't collapse during drag
- [x] Multiple drags work consecutively

**Question Drag-and-Drop**:
- [x] Expand section first
- [x] Drag question by ⋮ handle → Moves
- [x] Questions move between sections
- [x] Section stays open after move
- [x] Questions can be dragged to unassigned area

**Performance**:
- [x] Sortable only initialized for expanded sections
- [x] No unnecessary reloads
- [x] Smooth animations
- [x] No lag when toggling sections

## Technical Details

### State Preservation Pattern

This pattern is useful for any component that needs to reload data but preserve UI state:

```javascript
// Generic pattern
async reloadData(preserveState = false) {
    // 1. Save current state
    const stateMap = new Map();
    if (preserveState) {
        this.items.forEach(item => {
            stateMap.set(item.id, {
                // Save whatever state you need
                isOpen: item.isOpen,
                isEditing: item.isEditing,
                selectedTab: item.selectedTab
            });
        });
    }
    
    // 2. Fetch fresh data
    const newData = await fetchFromServer();
    
    // 3. Restore state
    this.items = newData.map(item => {
        const saved = stateMap.get(item.id);
        return {
            ...item,
            isOpen: saved ? saved.isOpen : defaultValue,
            isEditing: saved ? saved.isEditing : false,
            selectedTab: saved ? saved.selectedTab : 0
        };
    });
}
```

### Sortable.js Configuration

**Important Options**:
- `handle` - Element that triggers drag (e.g., grip icon)
- `draggable` - Elements that can be dragged
- `filter` - Elements to ignore
- `group` - Allows dragging between lists
- `animation` - Smooth transitions
- `ghostClass` - Style for placeholder
- `dragClass` - Style for dragged item

**Common Mistakes**:
```javascript
// ❌ BAD: Everything is draggable
new Sortable(list, {
    onEnd: () => {}
});
// Result: Click anywhere drags, buttons don't work

// ✅ GOOD: Only handle is draggable
new Sortable(list, {
    handle: '.drag-handle',
    draggable: '.item',
    onEnd: () => {}
});
// Result: Only grip icon drags, everything else works
```

### Alpine.js $nextTick

`$nextTick()` waits for DOM to update before running code:

```javascript
// ❌ BAD: Sortable initialized before DOM exists
section.expanded = true;
initSortable();  // DOM not updated yet, listEl doesn't exist

// ✅ GOOD: Wait for DOM
section.expanded = true;
this.$nextTick(() => {
    initSortable();  // DOM updated, listEl exists
});
```

## Performance Improvements

### Before Fix
- ❌ Sortable initialized for all sections (even collapsed)
- ❌ Full reload after every operation
- ❌ Sections flash open/closed
- ❌ Lag when many sections

### After Fix
- ✅ Sortable only for expanded sections
- ✅ Minimal reloads (only when needed)
- ✅ Sections maintain state
- ✅ Smooth even with 20+ sections

## Debugging Tips

### Check Sortable Instance
```javascript
// In browser console
document.querySelectorAll('.questions-list').forEach(el => {
    console.log('Element:', el);
    console.log('Has Sortable:', el.Sortable);
});
```

### Check Alpine State
```javascript
// In browser console
Alpine.raw($refs.sectionsContainer);  // Check data
```

### Monitor State Changes
```javascript
// Add to loadData()
console.log('Loading data, preserveState:', preserveState);
console.log('Before:', this.sections.map(s => ({id: s.id, expanded: s.expanded})));
// ... load ...
console.log('After:', this.sections.map(s => ({id: s.id, expanded: s.expanded})));
```

## Conclusion

Fixed section state persistence and drag-and-drop by:
1. ✅ Preserving expanded/collapsed state across reloads
2. ✅ Configuring Sortable.js with proper selectors
3. ✅ Only initializing Sortable for visible elements
4. ✅ Reinitializing Sortable when sections expand
5. ✅ Avoiding unnecessary data reloads

Users can now:
- Drag sections smoothly without state loss
- Keep sections open while working
- Drag questions between sections
- Experience smooth, predictable behavior

**Status**: ✅ Fully Resolved  
**Risk**: Low - Standard state management pattern  
**Performance**: Significantly improved
