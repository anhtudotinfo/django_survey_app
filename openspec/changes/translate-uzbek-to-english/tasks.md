# Implementation Tasks: Translate Uzbek to English

## 1. Backend Model Translation

- [x] 1.1 Translate Direction model (models.py lines 74-78)
  - [x] `name` field verbose_name: `nomi` → `name`
  - [x] verbose_name_plural: `O'quv kurslari` → `Directions`

- [x] 1.2 Translate Survey model (models.py lines 86-108)
  - [x] `name` field: `nomi` → `name`
  - [x] `description` field: `ta'rif` → `description`
  - [x] `editable` field and help_text
  - [x] `deletable` field and help_text
  - [x] `duplicate_entry` field and help_text
  - [x] `private_response` field and help_text
  - [x] `can_anonymous_user` field and help_text
  - [x] `notification_to` field and help_text
  - [x] `success_page_content` field and help_text
  - [x] verbose_name_plural: `So'rovnomalar` → `Surveys`

- [x] 1.3 Translate Section model (models.py lines 149-155)
  - [x] `name` field: `nomi` → `name`
  - [x] `description` field: `ta'rif` → `description`
  - [x] `ordering` field: `tartib` → `ordering`
  - [x] verbose_name_plural: `Bo'limlar` → `Sections`

- [x] 1.4 Translate Question model (models.py lines 164-192)
  - [x] `type_field`: `kiritish maydonining turi` → `field type`
  - [x] `key` field and help_text
  - [x] `label` field and help_text: `Yorliq` → `label`
  - [x] `choices` field and help_text: `variantlar` → `choices`
  - [x] `help_text` field and help_text: `yordam matni` → `help text`
  - [x] `required` field and help_text: `talab qilinadi` → `required`
  - [x] `ordering` field and help_text: `variantlar` → `ordering`
  - [x] verbose_name_plural: `Savollar` → `Questions`

- [x] 1.5 Translate UserAnswer model (models.py lines 213-214)
  - [x] verbose_name_plural: `Foydalanuvchi javoblari` → `User Answers`

- [x] 1.6 Translate Answer model (models.py lines 234-235)
  - [x] verbose_name_plural: `Javoblar` → `Answers`

- [x] 1.7 Translate Question2 model (Rating system, models.py lines 513-535)
  - [x] `key` field and help_text
  - [x] `choices` field: `variantlar` → `choices`
  - [x] `help_text` field: `yordam matni` → `help text`
  - [x] `required` field and help_text
  - [x] `ordering` field and help_text
  - [x] verbose_name_plural: `Reyting savollari` → `Rating Questions`

- [x] 1.8 Translate UserAnswer2 model (models.py lines 563-564)
  - [x] verbose_name_plural: `Foydalanuvchi reyting javoblari` → `User Rating Answers`

- [x] 1.9 Translate UserRating model (models.py line 577)
  - [x] verbose_name_plural: `O'qituvchilar reytingi` → `Teacher Ratings`

- [x] 1.10 Translate Answer2 model (models.py lines 590-591)
  - [x] verbose_name_plural: `Reyting javoblari` → `Rating Answers`

## 2. Backend Validator Translation

- [x] 2.1 Translate RatingValidator error messages (validators.py lines 64, 69, 74)
  - [x] Line 64: `%ss son emas` → `%s is not a number`
  - [x] Line 69: `Qiymat ruxsat...` → `Value must not exceed the maximum allowed rating`
  - [x] Line 74: `Qiymat 1 dan kam...` → `Value must not be less than 1`

## 3. Backend Views Translation

- [x] 3.1 Translate success page title (views.py line 448)
  - [x] `Muvaffaqiyatli yuborildi!` → `Successfully submitted!`

## 4. Backend Forms Translation

- [x] 4.1 Translate form error message (forms.py line 124)
  - [x] `Bu maydon to'ldirilishi shart` → `This field is required`
  - [x] Wrap with `_()` for proper i18n

## 5. Backend Admin Views Translation

- [x] 5.1 Translate CSV export headers (admins/views.py lines 224, 226)
  - [x] Line 224: `foydalanuvchi` → `user`
  - [x] Line 226: `kurs nomi` → `course name`

## 6. Backend Comments Translation

- [x] 6.1 Translate comments (summary.py lines 427, 440)
  - [x] Line 427: Uzbek comment → English comment
  - [x] Line 440: Uzbek comment → English comment

- [x] 6.2 Translate comments (accounts/views.py line 131)
  - [x] Uzbek comment → English comment

## 7. Frontend Template Translation

- [x] 7.1 Translate success page (djf_surveys/templates/djf_surveys/success-page.html)
  - [x] Line 18: `Ushbu so'rovnomani to'ldirganingiz uchun tashakkur` → `Thank you for completing this survey`
  - [x] Line 23: Long Uzbek message → English message about appreciation
  - [x] Line 28: `Ortga` → `Back`

- [x] 7.2 Translate profile templates
  - [x] templates/accounts/profile.html line 56: `Kafedra(sikl) nomi` → `Department Name`
  - [x] templates/accounts/superuser_profile.html line 56: `Kafedra(sikl) nomi` → `Department Name`

- [x] 7.3 Translate users list template
  - [x] templates/accounts/users_list.html line 86: `Kafedra(sikl) nomi` → `Department Name`

- [x] 7.4 Translate admin directions template
  - [x] djf_surveys/templates/djf_surveys/admins/directions.html line 15: `Kurs nomi` → `Course Name`

## 8. Testing

- [x] 8.1 Test admin interface with English labels
  - [x] Navigate all model admins (Surveys, Sections, Questions, etc.)
  - [x] Verify labels display correctly
  - [x] Check inline forms
  - [x] Test filtering and search

- [x] 8.2 Test user-facing pages
  - [x] Submit a survey and verify success page
  - [x] Check error messages display correctly
  - [x] Test form validation messages

- [x] 8.3 Test profile pages
  - [x] View user profile
  - [x] View superuser profile
  - [x] Check users list

- [x] 8.4 Verify no functionality broken
  - [x] Survey creation
  - [x] Question adding
  - [x] Section management
  - [x] Response submission
  - [x] CSV export

- [x] 8.5 Check for any missed Uzbek text
  - [x] Search codebase for common Uzbek words
  - [x] Visual inspection of all admin pages
  - [x] Check all error scenarios

## 9. Documentation Review (Optional)

- [x] 9.1 Review ADMIN_GUIDE.md
  - [x] Check if Vietnamese text should be kept or translated
  - [x] Update any Uzbek references

- [x] 9.2 Review GUEST_SURVEY_SUMMARY.md
  - [x] Check Vietnamese text
  - [x] Update if needed

- [x] 9.3 Update UZBEK_TEXT_FINDINGS.md
  - [x] Mark all items as completed
  - [x] Add final status notes

## 10. Django i18n Setup (Optional Phase 2)

- [x] 10.1 Create locale directory structure
  - [x] `mkdir -p locale/uz/LC_MESSAGES`
  - [x] Configure LOCALE_PATHS in settings.py

- [x] 10.2 Extract translatable strings
  - [x] Run: `django-admin makemessages -l uz`
  - [x] Review generated .po file

- [x] 10.3 Add Uzbek translations
  - [x] Translate all msgid to msgstr in .po file
  - [x] Use translations from UZBEK_TEXT_FINDINGS.md

- [x] 10.4 Compile messages
  - [x] Run: `django-admin compilemessages`
  - [x] Verify .mo file created

- [x] 10.5 Configure language settings
  - [x] Add to LANGUAGES in settings.py
  - [x] Add LocaleMiddleware
  - [x] Add language selector to templates

- [x] 10.6 Test language switching
  - [x] Switch to Uzbek and verify translations
  - [x] Switch to English and verify
  - [x] Test with different browsers

## Dependencies

- Tasks 1.x must be completed before testing (8.x)
- Tasks 2.x-7.x can be done in parallel
- Task 10.x (i18n setup) is optional and independent

## Estimated Timeline

- **Phase 1 (Translation)**: 3-4 hours
  - Backend models: 2 hours (systematic translation)
  - Backend validators/views/forms: 30 minutes
  - Frontend templates: 30 minutes
  - Testing: 1 hour

- **Phase 2 (i18n Setup - Optional)**: 2-3 hours
  - Setup: 30 minutes
  - Translation: 1-2 hours
  - Testing: 30 minutes

**Total**: 3-7 hours (depending on whether Phase 2 included)

## Validation Checklist

Before marking as complete:
- [x] All 57 Uzbek text instances translated
- [x] No Uzbek text visible in admin interface
- [x] No Uzbek text visible in user-facing pages
- [x] All existing functionality works
- [x] No new errors or warnings
- [x] Code follows Django i18n conventions
- [x] Reference document (UZBEK_TEXT_FINDINGS.md) accurate

## Rollback Plan

If issues arise:
1. Git revert to previous commit
2. Restore from backup if database affected (not expected)
3. Fix specific issues and redeploy

No database changes, so rollback is safe and simple.
