# Design: Translate Uzbek to English

## Context

The Django Survey Application currently has Uzbek text embedded throughout the codebase:
- **Discovered**: Comprehensive audit revealed ~57 instances across backend and frontend
- **Location**: Models, validators, views, forms, templates
- **Impact**: Affects code readability, maintainability, and international collaboration
- **Documentation**: Recently created comprehensive English documentation creates language mismatch

**Stakeholders**:
- Developers (current and future contributors)
- System administrators (using Django admin interface)
- End users (seeing template messages)
- Documentation readers

**Constraints**:
- Must not break existing functionality
- Must not require database migrations
- Should follow Django i18n best practices
- Should be deployable independently

## Goals / Non-Goals

### Goals
1. **Translate all user-visible Uzbek text to English**
   - Model verbose_name and help_text
   - Validation error messages
   - Template strings
   - Admin interface labels

2. **Maintain Django i18n framework usage**
   - Keep `_()` wrapper for translations
   - Keep `{% trans %}` in templates
   - Enable future localization

3. **Improve code maintainability**
   - English field names and labels
   - Consistent with documentation
   - Industry-standard conventions

4. **Zero functionality changes**
   - No behavior changes
   - No database schema changes
   - No API changes

### Non-Goals
1. **Not translating migration files** (historical record)
2. **Not translating third-party library files** (myenv/)
3. **Not changing database data** (user-entered content)
4. **Not implementing full i18n in Phase 1** (optional Phase 2)
5. **Not translating documentation** (ADMIN_GUIDE.md may be intentionally multilingual)

## Decisions

### Decision 1: Translate Code to English, Keep i18n Framework

**Options Considered**:

**A) Remove i18n framework entirely, hard-code English**
- Pros: Simpler code, no translation overhead
- Cons: Cannot support other languages later, loses flexibility
- **Rejected**: Loses localization capability

**B) Keep Uzbek as primary, add English via locale files**
- Pros: No code changes needed
- Cons: Non-standard (English is convention), harder for international devs
- **Rejected**: Against industry standards

**C) Translate code to English, keep i18n framework (CHOSEN)**
- Pros: Industry standard, maintains i18n capability, improves readability
- Cons: Requires code changes
- **Benefits**: Can add Uzbek (or any language) back via locale files

**Decision**: Option C - Translate to English in code, optionally create Uzbek locale files

### Decision 2: Systematic Find-Replace Approach

**Approach**:
1. Use UZBEK_TEXT_FINDINGS.md as authoritative reference
2. Process files systematically (models → validators → views → templates)
3. Verify each change before committing
4. Test after each major section

**Why**: Minimizes errors, trackable progress, easy to verify completeness

### Decision 3: Two-Phase Implementation

**Phase 1 (Required)**: Code Translation
- Update all Python and template files
- Test functionality
- Deploy

**Phase 2 (Optional)**: i18n Setup
- Create locale directories
- Generate .po files
- Add Uzbek translations
- Enable language switching

**Why**: Allows immediate value (English code) without requiring full i18n setup

### Decision 4: Translation Mappings

**Standardized translations** (avoid inconsistency):

| Uzbek | English | Context |
|-------|---------|---------|
| nomi | name | Field name |
| ta'rif | description | Description field |
| tartib | ordering | Order/sequence field |
| kalit | key | Unique identifier |
| Yorliq | label | Display label |
| variantlar | choices | Options/choices |
| yordam matni | help text | Help/hint text |
| talab qilinadi | required | Required field |
| kiritish maydonining turi | field type | Input field type |
| tahrirlanadigan | editable | Can edit |
| o'chirib tashlasa bo'ladigan | deletable | Can delete |
| Anonymous yuborish | allow anonymous | Anonymous access |
| foydalanuvchi | user | User |
| javob | answer | Response/answer |
| savol | question | Question |
| So'rovnoma | survey | Survey |
| Bo'lim | section | Section |

### Decision 5: Testing Strategy

**Testing Levels**:
1. **Unit Level**: Verify text changes in models
2. **Integration Level**: Admin interface navigation
3. **User Level**: Survey submission flow
4. **Visual Level**: Manual inspection of all pages

**No automated test updates needed**: Text changes don't affect test logic

## Technical Implementation

### File-by-File Strategy

#### 1. Backend Models (djf_surveys/models.py)

**Approach**: Use MultiEdit tool for multiple changes per model

**Example for Survey model**:
```python
# Before
name = models.CharField(_("nomi"), max_length=200)
editable = models.BooleanField(_("tahrirlanadigan"), default=True,
    help_text=_("Agar belgi qo'yilmasa, foydalanuvchi yozuvni tahrirlay olmaydi."))

# After
name = models.CharField(_("name"), max_length=200)
editable = models.BooleanField(_("editable"), default=True,
    help_text=_("If unchecked, users cannot edit their responses."))
```

**Process**:
1. Read model class
2. Identify all Uzbek strings
3. Apply MultiEdit with all changes at once
4. Verify with Read tool

#### 2. Backend Validators (djf_surveys/validators.py)

**Simple Edit approach** (only 3 changes):
```python
# Before
raise ValidationError(_('%ss son emas.' % value))

# After
raise ValidationError(_('%s is not a number.' % value))
```

#### 3. Frontend Templates

**Template-specific considerations**:
- Preserve HTML structure
- Keep `{% trans %}` tags
- Update only the translatable strings

```html
<!-- Before -->
{% trans "Ushbu so'rovnomani to'ldirganingiz uchun tashakkur" %}

<!-- After -->
{% trans "Thank you for completing this survey" %}
```

### i18n Architecture (Phase 2 - Optional)

If implementing full i18n:

```
django_survey_app/
├── locale/
│   ├── uz/
│   │   └── LC_MESSAGES/
│   │       ├── django.po    # Uzbek translations
│   │       └── django.mo    # Compiled translations
│   └── en/
│       └── LC_MESSAGES/
│           └── django.po    # English (default)
├── djf_surveys/
│   └── locale/             # App-specific translations (optional)
└── settings.py             # LANGUAGES, LOCALE_PATHS config
```

**settings.py configuration**:
```python
LANGUAGE_CODE = 'en'  # Default language

LANGUAGES = [
    ('en', 'English'),
    ('uz', 'Uzbek'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

MIDDLEWARE = [
    'django.middleware.locale.LocaleMiddleware',  # Add this
    # ... other middleware
]
```

**Translation workflow**:
1. Extract: `django-admin makemessages -l uz`
2. Translate: Edit `locale/uz/LC_MESSAGES/django.po`
3. Compile: `django-admin compilemessages`
4. Deploy: Include .mo files in deployment

## Risks / Trade-offs

### Risk 1: Breaking Admin Interface for Uzbek-Speaking Users
**Impact**: Medium
**Probability**: High (certain to happen)
**Mitigation**:
- Create quick reference guide (Uzbek → English mapping)
- Can implement Phase 2 (i18n) to restore Uzbek interface
- Most admins likely understand basic English technical terms

### Risk 2: Missing Some Uzbek Instances
**Impact**: Low (cosmetic only)
**Probability**: Low (comprehensive search completed)
**Mitigation**:
- UZBEK_TEXT_FINDINGS.md has complete list
- Visual testing will catch any missed items
- Easy to fix in follow-up if found

### Risk 3: Translation Quality
**Impact**: Low
**Probability**: Medium
**Mitigation**:
- Using standard Django terminology
- Reference Django's own translations
- Can improve translations iteratively

### Risk 4: Deployment Timing
**Impact**: Low
**Probability**: Low
**Mitigation**:
- Non-breaking change, can deploy anytime
- No database migration needed
- Can bundle with other changes or deploy separately

## Trade-offs

| Aspect | Trade-off | Decision |
|--------|-----------|----------|
| **Immediate usability** | Uzbek users lose familiar labels | Accept: English is standard, can restore via i18n |
| **Implementation time** | Quick translation vs full i18n | Two-phase: translate first, i18n later |
| **Code consistency** | Mixed languages vs pure English | Pure English: better for international team |
| **Flexibility** | Hard-coded vs localizable | Localizable: keep i18n framework |

## Migration Plan

### Pre-Deployment
1. Complete all translations in development
2. Test thoroughly in local environment
3. Review changes via git diff
4. Create backup (though no DB changes)

### Deployment Steps
1. **Merge changes** to main branch
2. **Deploy** to staging
3. **Smoke test** admin interface and user flows
4. **Deploy** to production
5. **Monitor** for any issues

### Post-Deployment
1. **Communicate** changes to admin users
2. **Provide** quick reference guide if needed
3. **Monitor** for any missed Uzbek text
4. **Plan** Phase 2 (i18n) if needed

### Rollback Procedure
**If issues occur:**
```bash
# Simple git revert (no DB involved)
git revert <commit-hash>
git push
# Redeploy previous version
```

**Recovery time**: < 5 minutes (simple code change)

## Open Questions

### Q1: Should we implement full i18n (Phase 2) immediately?
**Options**:
- A) Translate only (Phase 1) and add i18n later if needed
- B) Implement full i18n immediately

**Recommendation**: Option A
- **Reasoning**: Gets immediate value (English code), i18n can be added anytime
- **Decision Point**: After Phase 1 deployment, assess if Uzbek UI is needed

### Q2: How to handle ADMIN_GUIDE.md multilingual content?
**Current State**: Contains Vietnamese sections
**Options**:
- A) Keep multilingual (intentional)
- B) English only, create separate Vietnamese guide
- C) Translate all to English

**Recommendation**: Option A (keep as-is)
- **Reasoning**: May be intentional for multilingual audience
- **Decision**: Review separately from code translation

### Q3: Should comments be translated?
**Current State**: 2-3 Uzbek comments in code
**Options**:
- A) Translate all comments to English
- B) Keep as-is

**Recommendation**: Option A
- **Reasoning**: Code comments should match code language
- **Effort**: Minimal (only 2-3 instances)

## Validation

### Definition of Done
- [ ] All 57 Uzbek instances identified and translated
- [ ] Admin interface displays English labels
- [ ] User-facing pages display English text
- [ ] No functionality broken
- [ ] No errors in console or logs
- [ ] All existing tests pass
- [ ] Code follows Django i18n conventions

### Testing Checklist
- [ ] Create survey in admin
- [ ] Add sections and questions
- [ ] Configure branch rules
- [ ] Submit survey as user
- [ ] View success page
- [ ] Export CSV
- [ ] Check profile pages
- [ ] Review users list
- [ ] Test all field types
- [ ] Verify error messages

## Alternative Approaches Considered

### Alternative 1: Use Machine Translation API
**Approach**: Use Google Translate API for automatic translation
**Pros**: Fast, consistent
**Cons**: Quality issues, costs, overkill for 57 strings
**Rejected**: Manual translation is better quality and simple enough

### Alternative 2: Create Parallel Uzbek/English Models
**Approach**: Keep Uzbek code, create English versions alongside
**Pros**: No breaking changes
**Cons**: Code duplication, maintenance nightmare
**Rejected**: Violates DRY principle

### Alternative 3: Database-Driven Labels
**Approach**: Store all labels in database, allow admin customization
**Pros**: Ultimate flexibility
**Cons**: Massive over-engineering, performance impact
**Rejected**: Inappropriate for this use case

## Success Metrics

### Immediate (Post-Phase 1)
- ✓ Zero Uzbek text in codebase (verified by search)
- ✓ All admin pages display English
- ✓ All user pages display English
- ✓ No functionality regressions
- ✓ No increase in error rates

### Long-term (3 months)
- Improved developer onboarding time
- International contributors able to understand code
- Reduced confusion in code reviews
- Consistent with documentation language

## References

- **Detailed Findings**: UZBEK_TEXT_FINDINGS.md
- **Django i18n Documentation**: https://docs.djangoproject.com/en/stable/topics/i18n/
- **Translation Best Practices**: https://docs.djangoproject.com/en/stable/topics/i18n/translation/
- **Django Model Field Reference**: https://docs.djangoproject.com/en/stable/ref/models/fields/
- **PEP 8 Style Guide**: https://pep8.org/ (English code comments)
