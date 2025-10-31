# Survey Internationalization (i18n) Specification

## MODIFIED Requirements

### Requirement: Model Field Labels
All Django model fields SHALL use English for verbose_name and help_text, following Django i18n conventions.

**Rationale**: English is the industry standard for code, even when using translation frameworks. This enables international collaboration while maintaining localization capability through Django's i18n system.

#### Scenario: Admin displays English field names
- **GIVEN** a survey administrator accesses the Django admin interface
- **WHEN** they view the Survey, Section, Question, or Answer models
- **THEN** all field labels SHALL be displayed in English
- **AND** all help text SHALL be in English
- **AND** the interface SHALL remain fully functional

#### Scenario: Error messages in English
- **GIVEN** a user submits invalid data
- **WHEN** validation occurs
- **THEN** error messages SHALL be displayed in English
- **AND** messages SHALL be clear and actionable

### Requirement: Template Strings
All user-facing template strings SHALL use English wrapped in Django translation tags.

**Rationale**: Separates content from code, enables easy localization through .po files.

#### Scenario: Success page displays English
- **GIVEN** a user completes a survey
- **WHEN** they are redirected to the success page
- **THEN** the thank you message SHALL be displayed in English
- **AND** navigation elements SHALL be in English

#### Scenario: Profile page labels in English
- **GIVEN** a user views their profile
- **WHEN** the page renders
- **THEN** all form labels SHALL be displayed in English
- **AND** particularly the "Department Name" field SHALL be in English

## ADDED Requirements

### Requirement: Translation Framework Compliance
The codebase SHALL comply with Django i18n best practices for future localization.

**Rationale**: Maintains ability to add translations for any language through Django's locale system without code changes.

#### Scenario: Strings are translation-ready
- **GIVEN** a developer wants to add Uzbek translations
- **WHEN** they run `django-admin makemessages -l uz`
- **THEN** all user-visible strings SHALL be extracted to .po file
- **AND** strings SHALL be properly wrapped with `_()` or `{% trans %}`
- **AND** no strings SHALL be hard-coded without translation tags

#### Scenario: Locale files can be added
- **GIVEN** an administrator wants to support Uzbek language
- **WHEN** they create locale/uz/LC_MESSAGES/django.po
- **AND** translate the strings
- **AND** compile with `django-admin compilemessages`
- **THEN** the interface SHALL display in Uzbek when language is selected
- **AND** no code changes SHALL be required

### Requirement: Code Comment Language
All code comments SHALL be written in English.

**Rationale**: Consistency with code language, international collaboration.

#### Scenario: Comments are readable by international developers
- **GIVEN** a developer reviews the codebase
- **WHEN** they read code comments
- **THEN** all comments SHALL be in English
- **AND** comments SHALL explain logic clearly
- **AND** no Uzbek or other non-English comments SHALL exist

## REMOVED Requirements

### Requirement: Uzbek as Primary Code Language
**Removed**: Using Uzbek text directly in model fields, error messages, and templates.

**Reason**: Non-standard practice that hinders international collaboration and code maintainability.

**Migration**: All Uzbek text translated to English. Original Uzbek translations can be restored via Django i18n locale files if needed.

#### Previous behavior (now removed)
- Model fields had Uzbek verbose_name like `nomi`, `ta'rif`, `tartib`
- Error messages were in Uzbek
- Template strings were in Uzbek
- Help text was in Uzbek

## Implementation Notes

### Translation Mapping Reference

Common translations from Uzbek to English:
- `nomi` → `name`
- `ta'rif` → `description`
- `tartib` → `ordering`
- `kalit` → `key`
- `Yorliq` → `label`
- `variantlar` → `choices`
- `yordam matni` → `help text`
- `talab qilinadi` → `required`
- `So'rovnomalar` → `Surveys`
- `Bo'limlar` → `Sections`
- `Savollar` → `Questions`
- `Javoblar` → `Answers`

### Files Affected

**Backend (Python)**:
- `djf_surveys/models.py` - 40+ field definitions
- `djf_surveys/validators.py` - 3 error messages
- `djf_surveys/views.py` - 1 page title
- `djf_surveys/forms.py` - 1 error message
- `djf_surveys/admins/views.py` - 2 CSV headers
- `djf_surveys/summary.py` - 2 comments

**Frontend (Templates)**:
- `djf_surveys/templates/djf_surveys/success-page.html` - 3 strings
- `templates/accounts/profile.html` - 1 label
- `templates/accounts/superuser_profile.html` - 1 label
- `templates/accounts/users_list.html` - 1 header
- `djf_surveys/templates/djf_surveys/admins/directions.html` - 1 header

### Backward Compatibility

This change is **100% backward compatible**:
- No database schema changes
- No migrations required
- No functionality changes
- Only display text changes
- Existing data unaffected
- Admin can optionally add Uzbek via locale files

### Testing Requirements

Must verify:
1. All admin pages display correctly
2. All user-facing pages display correctly
3. Error messages display correctly
4. No Uzbek text remains visible
5. All existing functionality works
6. No new errors or warnings

### Future Enhancements

Optional Phase 2 (not part of this change):
- Create `locale/uz/LC_MESSAGES/` directory structure
- Generate `.po` files for Uzbek translations
- Compile message catalogs
- Add language selector to UI
- Enable multi-language support

This would restore Uzbek interface while maintaining English code.
