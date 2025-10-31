# Uzbek Text Findings - Translation Needed

## Overview
This document lists all Uzbek text found in the Django Survey Application that should be translated to English for internationalization.

---

## 1. Backend (Python Files)

### djf_surveys/models.py

#### Direction Model (Line 74-78)
```python
# CURRENT (Uzbek):
name = models.CharField(_("nomi"), max_length=255)
verbose_name_plural = _("O'quv kurslari")

# SHOULD BE (English):
name = models.CharField(_("name"), max_length=255)
verbose_name_plural = _("Directions")
```

#### Survey Model (Lines 86-108)
```python
# CURRENT (Uzbek):
name = models.CharField(_("nomi"), max_length=200)
description = models.TextField(_("ta'rif"), default='')
editable = models.BooleanField(_("tahrirlanadigan"), default=True,
    help_text=_("Agar belgi qo'yilmasa, foydalanuvchi yozuvni tahrirlay olmaydi."))
deletable = models.BooleanField(_("o'chirib tashlasa bo'ladigan"), default=True,
    help_text=_("Agar belgi qo'yilmasa, foydalanuvchi yozuvni o'chira olmaydi."))
duplicate_entry = models.BooleanField(_("bitta foydalanuvchi bir necha marta yuborish mumkin"), default=False,
    help_text=_("Agar belgi qo'yilsa, foydalanuvchi qayta topshirishi mumkin."))
private_response = models.BooleanField(_("xususiy javob"), default=False,
    help_text=_("Agar belgi qo'yilsa, faqat administrator va egasi kira oladi."))
can_anonymous_user = models.BooleanField(_("anonim yuborish"), default=False,
    help_text=_("Agar belgi qo'yilsa, autentifikatsiyasiz foydalanuvchi yuboradi."))
notification_to = models.TextField(_("Bildirishnoma"), blank=True, null=True,
    help_text=_("Xabardor qilish uchun elektron pochta manzilingizni kiriting"))
success_page_content = models.TextField(_("Muvaffaqiyatli yakunlash sahifasi mazmuni"), blank=True, null=True,
    help_text=_("Muvaffaqiyatli sahifasi shu yerda o'zgartirishingiz mumkin. HTML sintaksisi qo'llab-quvvatlanadi"))
verbose_name_plural = _("So'rovnomalar")

# SHOULD BE (English):
name = models.CharField(_("name"), max_length=200)
description = models.TextField(_("description"), default='')
editable = models.BooleanField(_("editable"), default=True,
    help_text=_("If unchecked, users cannot edit their responses."))
deletable = models.BooleanField(_("deletable"), default=True,
    help_text=_("If unchecked, users cannot delete their responses."))
duplicate_entry = models.BooleanField(_("allow multiple submissions"), default=False,
    help_text=_("If checked, users can submit the survey multiple times."))
private_response = models.BooleanField(_("private response"), default=False,
    help_text=_("If checked, only administrators and the owner can access responses."))
can_anonymous_user = models.BooleanField(_("allow anonymous submissions"), default=False,
    help_text=_("If checked, unauthenticated users can submit responses."))
notification_to = models.TextField(_("notification email"), blank=True, null=True,
    help_text=_("Enter email addresses to notify on submission"))
success_page_content = models.TextField(_("success page content"), blank=True, null=True,
    help_text=_("Customize the success page content. HTML syntax supported."))
verbose_name_plural = _("Surveys")
```

#### Section Model (Lines 149-155)
```python
# CURRENT (Uzbek):
name = models.CharField(_("nomi"), max_length=255)
description = models.TextField(_("ta'rif"), blank=True, default='')
ordering = models.PositiveIntegerField(_("tartib"), default=0)
verbose_name_plural = _("Bo'limlar")

# SHOULD BE (English):
name = models.CharField(_("name"), max_length=255)
description = models.TextField(_("description"), blank=True, default='')
ordering = models.PositiveIntegerField(_("ordering"), default=0)
verbose_name_plural = _("Sections")
```

#### Question Model (Lines 164-192)
```python
# CURRENT (Uzbek):
type_field = models.PositiveSmallIntegerField(_("kiritish maydonining turi"), choices=TYPE_FIELD_CHOICES)
key = models.CharField(_("kalit"), max_length=225, unique=True, null=True, blank=True,
    help_text=_("Noyob kalit savol matnidan avtomatik yaratiladi. Yaratishni istasangiz, bo'sh joyni to'ldiring."))
label = models.CharField(_("Yorliq"), max_length=500, help_text=_("Savolingizni shu yerga kiriting."))
choices = models.TextField(_("variantlar"), blank=True, null=True,
    help_text=_("Agar maydon turi radio, tanlanadigan yoki ko'p variantli bo'lsa, ajratilgan variantlarni to'ldiring"
               "vergullar bilan. Masalan: Erkak, Ayol"))
help_text = models.CharField(_("yordam matni"), max_length=200, blank=True, null=True,
    help_text=_("Bu yerda yordam matnini kiritishingiz mumkin."))
required = models.BooleanField(_("talab qilinadi"), default=True,
    help_text=_("Agar belgi qo'yilsa, foydalanuvchi ushbu savolga javob berishi kerak."))
ordering = models.PositiveIntegerField(_("variantlar"), default=0,
    help_text=_("So'rovnomalar doirasida savollar tartibini belgilaydi."))
verbose_name_plural = _("Savollar")

# SHOULD BE (English):
type_field = models.PositiveSmallIntegerField(_("field type"), choices=TYPE_FIELD_CHOICES)
key = models.CharField(_("key"), max_length=225, unique=True, null=True, blank=True,
    help_text=_("Unique key auto-generated from question text. Leave blank to auto-create."))
label = models.CharField(_("label"), max_length=500, help_text=_("Enter your question here."))
choices = models.TextField(_("choices"), blank=True, null=True,
    help_text=_("If field type is radio, select or multi-select, enter choices separated by commas. "
               "Example: Male, Female"))
help_text = models.CharField(_("help text"), max_length=200, blank=True, null=True,
    help_text=_("You can enter help text here."))
required = models.BooleanField(_("required"), default=True,
    help_text=_("If checked, users must answer this question."))
ordering = models.PositiveIntegerField(_("ordering"), default=0,
    help_text=_("Determines the order of questions within the survey."))
verbose_name_plural = _("Questions")
```

#### UserAnswer Model (Lines 213-214)
```python
# CURRENT (Uzbek):
verbose_name_plural = _("Foydalanuvchi javoblari")

# SHOULD BE (English):
verbose_name_plural = _("User Answers")
```

#### Answer Model (Lines 234-235)
```python
# CURRENT (Uzbek):
verbose_name_plural = _("Javoblar")

# SHOULD BE (English):
verbose_name_plural = _("Answers")
```

#### Question2 Model (Lines 513-535) - Rating System
```python
# CURRENT (Uzbek):
key = models.CharField(_("kalit"), ..., help_text=_("Noyob kalit savol matnidan avtomatik yaratiladi..."))
choices = models.TextField(_("variantlar"), ...)
help_text = models.CharField(_("yordam matni"), ...)
required = models.BooleanField(_("talab qilinadi"), ..., help_text=_("Agar belgi qo'yilsa, foydalanuvchi ushbu savolga javob berishi kerak."))
ordering = models.PositiveIntegerField(_("variantlar"), ..., help_text=_("So'rovnomalar doirasida savollar tartibini belgilaydi."))
verbose_name_plural = _("Reyting savollari")

# SHOULD BE (English):
key = models.CharField(_("key"), ..., help_text=_("Unique key auto-generated from question text..."))
choices = models.TextField(_("choices"), ...)
help_text = models.CharField(_("help text"), ...)
required = models.BooleanField(_("required"), ..., help_text=_("If checked, users must answer this question."))
ordering = models.PositiveIntegerField(_("ordering"), ..., help_text=_("Determines the order of questions within the survey."))
verbose_name_plural = _("Rating Questions")
```

#### UserAnswer2 Model (Lines 563-564)
```python
# CURRENT (Uzbek):
verbose_name_plural = _("Foydalanuvchi reyting javoblari")

# SHOULD BE (English):
verbose_name_plural = _("User Rating Answers")
```

#### UserRating Model (Line 577)
```python
# CURRENT (Uzbek):
verbose_name_plural = _("O'qituvchilar reytingi")

# SHOULD BE (English):
verbose_name_plural = _("Teacher Ratings")
```

#### Answer2 Model (Lines 590-591)
```python
# CURRENT (Uzbek):
verbose_name_plural = _("Reyting javoblari")

# SHOULD BE (English):
verbose_name_plural = _("Rating Answers")
```

---

### djf_surveys/validators.py (Lines 64, 69, 74)

```python
# CURRENT (Uzbek):
raise ValidationError(_('%ss son emas.' % value))
raise ValidationError(_('Qiymat ruxsat etilgan reytinglarning eng ko'p miqdoridan oshib ketmasligi lozim.'))
raise ValidationError(_('Qiymat 1 dan kam bo'lmasligi kerak.'))

# SHOULD BE (English):
raise ValidationError(_('%s is not a number.' % value))
raise ValidationError(_('Value must not exceed the maximum allowed rating.'))
raise ValidationError(_('Value must not be less than 1.'))
```

---

### djf_surveys/views.py (Line 448)

```python
# CURRENT (Uzbek):
title_page = _("Muvaffaqiyatli yuborildi!")

# SHOULD BE (English):
title_page = _("Successfully submitted!")
```

---

### djf_surveys/forms.py (Line 124)

```python
# CURRENT (Uzbek):
self.add_error(field_name, 'Bu maydon to'ldirilishi shart')

# SHOULD BE (English):
self.add_error(field_name, _('This field is required'))  # Also wrap with _() for translation
```

---

### djf_surveys/admins/views.py (Lines 224, 226)

```python
# CURRENT (Uzbek):
header.append('foydalanuvchi')
header.append('kurs nomi')

# SHOULD BE (English):
header.append('user')
header.append('course name')
```

---

### djf_surveys/summary.py (Lines 427, 440)

```python
# CURRENT (Uzbek - in comments):
# Barcha Question2 savollariga berilgan javoblarni umumlashtirib, foydalanuvchilarni o'rtacha reytinglari bilan ApexCharts bar chartini yaratadi.
# Har bir foydalanuvchi uchun o'rtacha reytingni hisoblash

# SHOULD BE (English):
# Summarizes all Question2 answers and creates an ApexCharts bar chart with users' average ratings.
# Calculate average rating for each user
```

---

## 2. Frontend (Template Files)

### djf_surveys/templates/djf_surveys/success-page.html (Lines 18, 23, 28)

```html
<!-- CURRENT (Uzbek): -->
{% trans "Ushbu so'rovnomani to'ldirganingiz uchun tashakkur" %}
{% trans "Sizning sa'y-harakatlaringiz va so'rovnomani to'ldirishga ajratgan vaqtingizni juda qadrlaymiz. Sizning javoblaringiz bizga yordam beradi." %}
{% trans "Ortga" %}

<!-- SHOULD BE (English): -->
{% trans "Thank you for completing this survey" %}
{% trans "We greatly appreciate your efforts and the time you spent filling out this survey. Your responses help us." %}
{% trans "Back" %}
```

---

### templates/accounts/profile.html (Line 56)

```html
<!-- CURRENT (Uzbek): -->
<label for="{{ p_form.department.id_for_label }}" class="block mb-1 font-medium text-gray-700">Kafedra(sikl) nomi</label>

<!-- SHOULD BE (English): -->
<label for="{{ p_form.department.id_for_label }}" class="block mb-1 font-medium text-gray-700">Department Name</label>
```

---

### templates/accounts/superuser_profile.html (Line 56)

```html
<!-- CURRENT (Uzbek): -->
<label for="{{ p_form.department.id_for_label }}" class="block mb-1 font-medium text-gray-700">Kafedra(sikl) nomi</label>

<!-- SHOULD BE (English): -->
<label for="{{ p_form.department.id_for_label }}" class="block mb-1 font-medium text-gray-700">Department Name</label>
```

---

### templates/accounts/users_list.html (Line 86)

```html
<!-- CURRENT (Uzbek): -->
<th class="px-1 py-1 text-left text-lg font-medium text-gray-500 uppercase tracking-wider">Kafedra(sikl) nomi</th>

<!-- SHOULD BE (English): -->
<th class="px-1 py-1 text-left text-lg font-medium text-gray-500 uppercase tracking-wider">Department Name</th>
```

---

### djf_surveys/templates/djf_surveys/admins/directions.html (Line 15)

```html
<!-- CURRENT (Uzbek): -->
<th class="px-1 py-1 text-left text-lg font-medium text-gray-500 uppercase tracking-wider">Kurs nomi</th>

<!-- SHOULD BE (English): -->
<th class="px-1 py-1 text-left text-lg font-medium text-gray-500 uppercase tracking-wider">Course Name</th>
```

---

### accounts/views.py (Line 131 - Comment)

```python
# CURRENT (Uzbek):
# Department nomi bo'yicha alfavit tartibida saralash

# SHOULD BE (English):
# Sort alphabetically by department name
```

---

## 3. Documentation Files

### ADMIN_GUIDE.md

**Multiple Vietnamese sections need translation to English:**

Line 29: `### 1. **Surveys** (So'rovnomalar)`
Line 52: `### 2. **Sections** (Bo'limlar) ⭐ MỚI`
Line 78: `### 3. **Questions** (Savollar)`
Line 176: `### 7. **Answers** (Javoblar)`
Line 193: `### 8. **Directions** (O'quv kurslari)`

**Note**: The ADMIN_GUIDE.md contains extensive Vietnamese text that should be reviewed separately. This appears to be intentional multi-language documentation.

---

### GUEST_SURVEY_SUMMARY.md

Line 109: `2. Vào **Surveys (So'rovnomalar)**`
Line 116: `2. Go to **Surveys (So'rovnomalar)**`

---

## 4. Migration Files

**Note**: Migration files contain historical Uzbek text in field definitions. These don't need to be changed as migrations are historical records. The important thing is to fix the current model definitions (already listed above).

---

## Summary Statistics

### Total Uzbek Text Instances Found:

**Backend (Python):**
- djf_surveys/models.py: ~40 instances
- djf_surveys/validators.py: 3 instances
- djf_surveys/views.py: 1 instance
- djf_surveys/forms.py: 1 instance
- djf_surveys/admins/views.py: 2 instances
- djf_surveys/summary.py: 2 comments

**Frontend (Templates):**
- success-page.html: 3 instances
- accounts templates: 3 instances
- admins templates: 1 instance

**Documentation:**
- ADMIN_GUIDE.md: 5+ instances (mostly Vietnamese, not Uzbek)
- GUEST_SURVEY_SUMMARY.md: 2 instances (Vietnamese)

**Total Backend Changes Needed**: ~50 instances
**Total Frontend Changes Needed**: ~7 instances
**Total Documentation Review Needed**: Multiple files with Vietnamese/mixed language

---

## Recommended Action Plan

### Priority 1: Backend Models (High Impact)
1. Update all model field verbose_name and help_text in `djf_surveys/models.py`
2. Update validators in `djf_surveys/validators.py`
3. Update view messages in `djf_surveys/views.py`
4. Update form error messages in `djf_surveys/forms.py`

### Priority 2: Frontend Templates (User-Facing)
1. Update success-page.html template strings
2. Update accounts profile templates
3. Update admin templates

### Priority 3: Code Comments
1. Update comments in summary.py
2. Update comments in views.py

### Priority 4: Documentation (Optional)
1. Review ADMIN_GUIDE.md for language consistency
2. Update GUEST_SURVEY_SUMMARY.md

### Translation Considerations

**For proper Django i18n:**
1. All user-facing strings should use `_("text")` or `{% trans "text" %}`
2. Create/update locale files for Uzbek translations
3. Keep English as the primary language in code
4. Uzbek translations should go in locale/uz/LC_MESSAGES/django.po

---

## Notes

1. **Migrations**: Historical migrations don't need updating (they're records of past changes)
2. **Virtual Environment**: Files in `myenv/` don't need changes (Django core translations)
3. **Vietnamese Text**: ADMIN_GUIDE.md contains significant Vietnamese content - this may be intentional for multi-language support
4. **Translation Framework**: The codebase already uses Django's translation framework `_()` and `{% trans %}`, which is good!

---

## Next Steps

Would you like me to:
1. Create a specification/proposal for this translation work using OpenSpec?
2. Begin making the actual code changes?
3. Create a translation mapping file for reference?
4. Set up proper Django i18n configuration?

**Recommendation**: Create an OpenSpec proposal first to document this change properly, then implement systematically.
