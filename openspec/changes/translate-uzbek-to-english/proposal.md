# Proposal: Translate Backend and Frontend from Uzbek to English

## Why

The codebase currently contains extensive Uzbek text throughout backend models, validators, views, forms, and frontend templates. This creates several issues:

- **International Collaboration**: Non-Uzbek-speaking developers cannot understand field names, error messages, and help text
- **Code Maintainability**: Mixed language codebase is harder to maintain and debug
- **Industry Standards**: English is the standard language for code, even when using Django's i18n framework
- **Documentation Mismatch**: Recent comprehensive documentation is in English, but code remains in Uzbek
- **Developer Experience**: IDE autocomplete, error messages, and debugging are less effective with non-English identifiers

**Current State**: ~57 instances of Uzbek text across backend and frontend

**Desired State**: English as primary language in code, with proper i18n setup allowing Uzbek translations via Django's locale framework.

## What Changes

### Backend Translation
- **Model Fields**: Translate all verbose_name, help_text in models.py (40+ changes)
- **Validators**: Translate 3 error messages in validators.py
- **Views**: Translate page titles and messages in views.py
- **Forms**: Translate error messages in forms.py
- **Admin**: Translate CSV headers in admins/views.py
- **Comments**: Translate Uzbek comments to English

### Frontend Translation
- **Success Page**: 3 user-facing messages
- **Account Templates**: Department/Kafedra labels in 3 files
- **Admin Templates**: Table headers

## Impact

### Affected Code Files
**Backend**: models.py (40+), validators.py (3), views.py (1), forms.py (1), admins/views.py (2)
**Frontend**: 5 template files (7 changes total)

### Breaking Changes
**None** - Display text only, no functionality changes

### Migration Path
1. Update Python files with English text
2. Test admin interface
3. Optional: Create Uzbek locale files for i18n

## Benefits
- Industry-standard English codebase
- Better IDE support and debugging
- Matches comprehensive English documentation
- Enables international collaboration

## Timeline
4-6 hours total (2-3h backend, 1h frontend, 1h testing)
