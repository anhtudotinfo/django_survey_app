# Design: Translate Frontend UI/UX to English

## Context

The Django Survey Application backend has been successfully translated to English (see `translate-uzbek-to-english`), but frontend templates still contain Uzbek text in:
- Navigation menus
- Page titles and headings  
- Form labels and buttons
- Modal dialogs
- Helper text and placeholders
- Empty states and messages

This creates an inconsistent user experience where the backend (admin, models, errors) is English but the frontend UI remains in Uzbek.

**Stakeholders**:
- End users (currently Uzbek-speaking, future: international)
- Administrators (using admin interface)
- Developers (testing, debugging, maintaining)
- Documentation writers (need matching screenshots)

**Constraints**:
- Must not break existing functionality
- Must maintain Django i18n framework
- Should be deployable independently
- Should enable future bilingual support

## Goals / Non-Goals

### Goals
1. **Translate all user-facing Uzbek text to English**
   - Navigation menus and links
   - Page titles and headings
   - Form labels, buttons, placeholders
   - Modal dialogs and confirmations
   - Help text and instructions
   - Empty states and messages

2. **Maintain i18n framework**
   - Keep all `{% trans %}` and `{% blocktrans %}` tags
   - Ensure new text is properly wrapped
   - Enable future Uzbek locale creation

3. **Ensure consistency**
   - Match backend terminology
   - Use standard UI conventions
   - Consistent capitalization and tone

4. **Zero functionality changes**
   - No behavior changes
   - No layout changes
   - No routing changes

### Non-Goals
1. **Not redesigning UI/UX** (layout, styling, components)
2. **Not changing functionality** (forms, validation, logic)
3. **Not implementing language switcher** (Phase 2 - future work)
4. **Not translating user-generated content** (survey data)
5. **Not modifying JavaScript logic** (unless text-related)

## Decisions

### Decision 1: Template-by-Template Translation Approach

**Chosen Approach**: Systematic file-by-file translation

**Why**:
- Easier to track progress
- Less likely to miss instances
- Clear checklist for validation
- Rollback is simple

**Implementation**:
1. Group templates by priority (auth > navigation > surveys > components)
2. Translate each file completely before moving to next
3. Test after each major group
4. Document all changes

**Alternatives Considered**:
- Pattern-based search/replace: Risk of missing context-specific translations
- Automated translation: Poor quality for UI text

### Decision 2: Translation Terminology

**Standard UI Terminology**:

| Uzbek | English | Context |
|-------|---------|---------|
| Bosh sahifa | Home | Main navigation |
| Kurslar | Courses | Course/direction list |
| O'qituvchilar ro'yxati | Teachers List | User list navigation |
| Tizimga kirish | Sign In | Login page heading |
| Kirish | Login | Login button |
| Eslab qolish | Remember me | Remember login checkbox |
| Natija | Results | Survey results |
| Izlash | Search | Search placeholder |
| Maydon turi | Field Type | Modal heading |
| Yopish | Close | Modal close button |
| Tasdiqnoma | Confirmation | Delete confirmation |
| Bu yerda hech narsa yo'q | Nothing here yet | Empty state |
| Ro'yxatdan o'tish | Register | Registration |
| Chiqish | Logout | Logout action |

**Why These Choices**:
- Standard web application conventions
- Matches industry terminology
- Clear and concise
- Consistent with backend translations

### Decision 3: i18n Tag Usage

**Guideline**: Always use Django translation tags

**For Simple Text**:
```html
<h1>{% trans "Sign In" %}</h1>
<button>{% trans "Login" %}</button>
```

**For Text with Variables**:
```html
{% blocktrans with name=survey.name %}Results - {{ name }}{% endblocktrans %}
```

**For Placeholders**:
```html
<input placeholder="{% trans 'Search...' %}">
```

**Why**:
- Enables future localization
- Django best practice
- Easy to generate .po files
- Type-safe with translation strings

### Decision 4: Priority-Based Implementation

**Priority Levels**:

**High Priority (Must-Have)**:
1. Authentication pages (login, register, logout)
2. Main navigation (master.html)
3. Survey pages (list, form, results)
4. Admin pages (summary, directions)

**Medium Priority (Should-Have)**:
1. Modal dialogs
2. Search components
3. Empty states
4. Profile pages

**Low Priority (Nice-to-Have)**:
1. 404 page
2. Widget templates
3. Button components (if they have text)

**Rationale**: User-facing pages first, components second, rarely-seen pages last

## Technical Implementation

### File Structure

```
Translation Changes by Directory:

templates/accounts/
├── login.html          [HIGH] - Login form
├── register.html       [HIGH] - Registration
├── logout.html         [HIGH] - Logout confirmation
├── profile.html        [MED]  - User profile
├── superuser_profile.html [MED] - Admin profile
├── users_list.html     [MED]  - Users listing
└── delete.html         [LOW]  - Account deletion

djf_surveys/templates/djf_surveys/
├── master.html         [HIGH] - Navigation menu
├── survey_list.html    [HIGH] - Survey listings
├── form.html           [HIGH] - Survey form
├── answer_list.html    [HIGH] - Results page
├── success-page.html   [DONE] - Already translated
├── detail_result.html  [MED]  - Result details
└── admins/
    ├── summary.html    [HIGH] - Analytics page
    ├── directions.html [HIGH] - Courses list
    ├── form.html       [MED]  - Survey editor
    └── ...

components/
├── search_form.html           [MED] - Search bar
├── modal_delete.html          [MED] - Delete confirmation
├── modal_choice_field_type.html [MED] - Field type modal
├── empty_state.html           [MED] - Empty message
├── section_progress.html      [LOW] - Progress indicator
└── draft_resume_banner.html   [LOW] - Draft banner
```

### Translation Patterns

#### Pattern 1: Page Headers
```html
<!-- Before -->
<h2 class="text-2xl font-bold mb-6 text-center">Tizimga kirish</h2>

<!-- After -->
<h2 class="text-2xl font-bold mb-6 text-center">{% trans "Sign In" %}</h2>
```

#### Pattern 2: Navigation Links
```html
<!-- Before -->
<a href="{% url 'djf_surveys:index' %}" class="...">Bosh sahifa</a>

<!-- After -->
<a href="{% url 'djf_surveys:index' %}" class="...">{% trans "Home" %}</a>
```

#### Pattern 3: Form Buttons
```html
<!-- Before -->
<button type="submit" class="...">Kirish</button>

<!-- After -->
<button type="submit" class="...">{% trans "Login" %}</button>
```

#### Pattern 4: Modal Headings
```html
<!-- Before -->
{% trans "Tasdiqnoma" %}

<!-- After -->
{% trans "Confirmation" %}
```

#### Pattern 5: Placeholders
```html
<!-- Before -->
placeholder="{% trans 'Izlash...' %}"

<!-- After -->
placeholder="{% trans 'Search...' %}"
```

#### Pattern 6: Block Trans with Variables
```html
<!-- Before -->
{% blocktrans with html='<span id="object_name" class="font-medium"/>' %}
Ushbu faylni o'chirmoqchimisiz: {{ html }}?
{% endblocktrans %}

<!-- After -->
{% blocktrans with html='<span id="object_name" class="font-medium"/>' %}
Do you want to delete this file: {{ html }}?
{% endblocktrans %}
```

### Testing Strategy

**Manual Testing**:
1. Authentication flow: login → register → logout
2. Survey flow: list → create/view → submit → results
3. Admin flow: dashboard → directions → summary
4. Navigation: all menu items → page titles match
5. Modals: delete confirmation → field type selector
6. Search: placeholder visible → results display
7. Empty states: no surveys → no results messages

**Automated Checks**:
```bash
# Check for remaining Uzbek text in templates
grep -r "[а-яА-ЯЎўҚқҒғҲҳ]" templates/ djf_surveys/templates/ \
  --include="*.html" --exclude-dir=migrations

# Verify all trans tags are valid
python manage.py makemessages --dry-run

# Check templates render
python manage.py check
```

**Visual Testing**:
- Take screenshots of all pages
- Compare with expected English text
- Verify no broken layouts
- Check responsive views (mobile/desktop)

## Risks / Trade-offs

### Risk 1: Inconsistent Terminology

**Risk**: Different pages using different terms for same concept
**Impact**: Medium (confusing for users)
**Mitigation**:
- Create terminology reference table
- Review all translations before committing
- Use consistent casing (Title Case for headings, Sentence case for body)

### Risk 2: Translation Context Loss

**Risk**: Short strings without context may be mistranslated
**Impact**: Low (most UI text is straightforward)
**Mitigation**:
- Review in actual page context
- Test all user flows
- Use Django's translation comments for ambiguous terms

### Risk 3: Missed Uzbek Instances

**Risk**: Some Uzbek text remains after translation
**Impact**: Low (cosmetic issue)
**Mitigation**:
- Systematic file-by-file approach
- Regex search for Cyrillic characters
- Visual inspection of all pages
- Checklist validation

### Risk 4: Breaking Django Trans Tags

**Risk**: Malformed `{% trans %}` tags cause template errors
**Impact**: High (breaks pages)
**Mitigation**:
- Test after each file
- Use `manage.py check` command
- Preview templates before committing

## Trade-offs

| Aspect | Trade-off | Decision |
|--------|-----------|----------|
| **Speed vs. Quality** | Fast bulk replace vs. careful review | Careful review: Better quality |
| **Completeness vs. Priority** | Translate everything vs. high-priority only | High-priority first: Faster value |
| **Consistency vs. Context** | Same translation always vs. context-specific | Context-specific: Better UX |
| **i18n Now vs. Later** | Implement locale files now vs. later | Later (Phase 2): Simpler rollout |

## Validation

### Definition of Done
- [ ] All authentication pages (login, register, logout) in English
- [ ] Main navigation menu in English
- [ ] All survey-related pages in English
- [ ] All admin pages in English
- [ ] All modal dialogs in English
- [ ] All search components in English
- [ ] All empty states in English
- [ ] Zero Uzbek text in user-facing templates
- [ ] All new text wrapped with `{% trans %}`
- [ ] All templates render without errors
- [ ] No functionality regressions

### Testing Checklist
- [ ] Login page displays correctly
- [ ] Register page displays correctly
- [ ] Logout works with English confirmation
- [ ] Navigation menu shows English labels
- [ ] Survey list shows English headers
- [ ] Survey form shows English labels
- [ ] Results page shows English headings
- [ ] Admin summary page shows English
- [ ] Directions/courses page shows English
- [ ] Delete modal shows English
- [ ] Search works with English placeholder
- [ ] Empty states show English messages
- [ ] All trans tags are valid
- [ ] No template syntax errors

## Migration Plan

### Pre-Deployment
1. Complete all high-priority translations
2. Test in local environment
3. Review screenshots of all pages
4. Verify no Uzbek text remains (regex check)
5. Run `python manage.py check`

### Deployment Steps
1. **Merge changes** to main branch
2. **Deploy** to staging environment
3. **Test** all user flows in staging
4. **Visual review** of all pages
5. **Deploy** to production
6. **Monitor** for issues

### Post-Deployment
1. **Communicate** changes to users
2. **Gather** feedback on translations
3. **Fix** any issues found
4. **Plan** Phase 2 (i18n/language switcher) if needed

### Rollback Procedure
```bash
# Simple git revert (no DB changes)
git revert <commit-hash>
git push
# Redeploy previous version
```
**Recovery time**: < 5 minutes

## Future Work (Phase 2 - Optional)

If bilingual support is needed:

1. **Create locale directory structure**
   ```bash
   mkdir -p locale/uz/LC_MESSAGES
   ```

2. **Generate translation files**
   ```bash
   django-admin makemessages -l uz
   ```

3. **Translate strings**
   - Edit `locale/uz/LC_MESSAGES/django.po`
   - Add Uzbek translations for all English strings

4. **Compile translations**
   ```bash
   django-admin compilemessages
   ```

5. **Add language switcher**
   - Update `settings.py` with LANGUAGES
   - Add language switcher to templates
   - Store user preference in session/cookie

6. **Configure middleware**
   ```python
   MIDDLEWARE = [
       'django.middleware.locale.LocaleMiddleware',
       # ...
   ]
   ```

## Success Metrics

### Immediate (Post-Deployment)
- ✓ Zero Uzbek text visible in UI
- ✓ All pages display correct English text
- ✓ No template errors or warnings
- ✓ No functionality broken
- ✓ All navigation links work

### Quality (Week 1)
- User can navigate entire site in English
- Screenshots for documentation are professional
- No user complaints about missing translations
- Developers can test without language barrier

### Long-term (Month 1)
- Positive user feedback on interface clarity
- Reduced developer onboarding time
- Easier maintenance and updates
- Foundation for multi-language support

## References

- **Related Work**: `openspec/changes/translate-uzbek-to-english/` (Backend translation)
- **Django Template i18n**: https://docs.djangoproject.com/en/stable/topics/i18n/translation/#internationalization-in-template-code
- **Translation Tags**: https://docs.djangoproject.com/en/stable/ref/templates/builtins/#trans
- **Block Translation**: https://docs.djangoproject.com/en/stable/ref/templates/builtins/#blocktrans
- **UI Writing Guide**: https://material.io/design/communication/writing.html
