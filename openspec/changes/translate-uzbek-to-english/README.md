# Translation Change: Uzbek to English

## Quick Summary

**Change ID**: `translate-uzbek-to-english`
**Status**: Proposed (awaiting approval)
**Effort**: 3-7 hours
**Risk**: Low (non-breaking, display text only)

This change translates all Uzbek text in the codebase to English, following Django i18n best practices.

## Why This Change

The codebase currently has ~57 instances of Uzbek text in:
- Model field labels and help text
- Error messages
- Template strings
- Admin interface labels

This creates issues for:
- International developers
- Code maintainability
- Documentation consistency (docs are in English)

## What's Changing

**Backend**: 47 instances across models, validators, views, forms
**Frontend**: 10 instances in templates
**Result**: English as primary language, Uzbek can be added via locale files

## Files in This Change

- **proposal.md** - Why and what (overview)
- **tasks.md** - Detailed implementation checklist (41 tasks)
- **design.md** - Technical decisions and architecture
- **specs/survey-i18n/spec.md** - Specification with requirements and scenarios
- **README.md** - This file

## Key Decisions

1. **Two-phase approach**: Translate first (Phase 1), optional i18n setup later (Phase 2)
2. **Keep i18n framework**: Strings still wrapped with `_()` and `{% trans %}`
3. **Standard translations**: Consistent English terms (see design.md)
4. **No breaking changes**: Display text only, zero functionality impact

## Implementation Plan

### Phase 1 (Required): Translation - 3-4 hours
1. Backend models (40+ changes) - 2 hours
2. Backend validators/views/forms - 30 min
3. Frontend templates - 30 min
4. Testing - 1 hour

### Phase 2 (Optional): i18n Setup - 2-3 hours
1. Create locale structure
2. Generate .po files
3. Add Uzbek translations
4. Enable language switching

## Validation

✅ **OpenSpec Validation**: Passed with `--strict` flag

```bash
openspec validate translate-uzbek-to-english --strict
# Result: Change 'translate-uzbek-to-english' is valid
```

## Next Steps

1. **Review** this proposal
2. **Approve** if acceptable
3. **Implement** following tasks.md checklist
4. **Test** thoroughly
5. **Deploy** (can deploy independently)

## References

- **Detailed Findings**: See `/UZBEK_TEXT_FINDINGS.md` in project root
- **All Uzbek Locations**: 57 instances documented with before/after
- **Django i18n Docs**: https://docs.djangoproject.com/en/stable/topics/i18n/

## Questions?

See `design.md` for:
- Technical decisions and rationale
- Risk analysis and mitigation
- Alternative approaches considered
- Testing strategy
- Rollback plan

See `tasks.md` for:
- Detailed step-by-step implementation
- 41 specific tasks organized by file
- Testing checklist
- Validation criteria

## Quick Start

To implement this change:

```bash
# 1. Review the proposal
cat openspec/changes/translate-uzbek-to-english/proposal.md

# 2. Review detailed tasks
cat openspec/changes/translate-uzbek-to-english/tasks.md

# 3. Start implementing (example for models.py)
# Follow tasks.md 1.1 through 1.10

# 4. Test as you go
python manage.py runserver
# Navigate to /moi-admin/ and verify English labels

# 5. When complete, validate
openspec validate translate-uzbek-to-english --strict
```

## Contact

For questions about this change proposal, refer to the OpenSpec documentation or review the design document.
