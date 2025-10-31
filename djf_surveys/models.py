import random
import string
from collections import namedtuple
from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.utils.text import slugify
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from accounts.models import Profile
from djf_surveys.utils import create_star


TYPE_FIELD = namedtuple(
    'TYPE_FIELD', 'text number radio select multi_select text_area url email date rating file'
)._make(range(11))


TYPE_FIELD_CHOICES = [
    (TYPE_FIELD.text, _("Text")),
    (TYPE_FIELD.number, _("Number")),
    (TYPE_FIELD.radio, _("Radio")),
    (TYPE_FIELD.select, _("Select")),
    (TYPE_FIELD.multi_select, _("Multi Select")),
    (TYPE_FIELD.text_area, _("Text Area")),
    (TYPE_FIELD.url, _("URL")),
    (TYPE_FIELD.email, _("Email")),
    (TYPE_FIELD.date, _("Date")),
    (TYPE_FIELD.rating, _("Rating")),
    (TYPE_FIELD.file, _("File Upload"))
]


def upload_survey_file(instance, filename):
    """Generate upload path for survey files."""
    import os
    from django.utils.text import get_valid_filename
    clean_filename = get_valid_filename(filename)
    return f'survey_uploads/{instance.user_answer.survey.id}/{instance.user_answer.id}/{clean_filename}'


def generate_unique_slug(klass, field, id, identifier='slug'):
    """
    Generate unique slug.
    """
    origin_slug = slugify(field)
    unique_slug = origin_slug
    numb = 1
    mapping = {
        identifier: unique_slug,
    }
    obj = klass.objects.filter(**mapping).first()
    while obj:
        if obj.id == id:
            break
        rnd_string = random.choices(string.ascii_lowercase, k=(len(unique_slug)))
        unique_slug = '%s-%s-%d' % (origin_slug, ''.join(rnd_string[:10]), numb)
        mapping[identifier] = unique_slug
        numb += 1
        obj = klass.objects.filter(**mapping).first()
    return unique_slug


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Direction(models.Model):
    name = models.CharField(_("name"), max_length=255)

    class Meta:
        verbose_name = _("direction")
        verbose_name_plural = _("Directions")
        ordering = ['name']

    def __str__(self):
        return self.name


class Survey(BaseModel):
    name = models.CharField(_("name"), max_length=200)
    description = models.TextField(_("ta’rif"), default='')
    slug = models.SlugField(_("slug"), max_length=225, default='')
    editable = models.BooleanField(_("editable"), default=True,
                                   help_text=_("Agar belgi qo‘yilmasa, foydalanuvchi yozuvni tahrirlay olmaydi."))
    deletable = models.BooleanField(_("o‘chirib tashlasa bo‘ladigan"), default=True,
                                    help_text=_("Agar belgi qo‘yilmasa, foydalanuvchi yozuvni o'chira olmaydi."))
    duplicate_entry = models.BooleanField(_("allow multiple submissions"), default=False,
                                          help_text=_("Agar belgi qo‘yilsa, foydalanuvchi qayta topshirishi mumkin."))
    private_response = models.BooleanField(_("private response"), default=False,
                                           help_text=_("Agar belgi qo‘yilsa, faqat administrator va egasi kira oladi."))
    can_anonymous_user = models.BooleanField(_("allow anonymous submissions"), default=False,
                                             help_text=_("Agar belgi qo‘yilsa, autentifikatsiyasiz foydalanuvchi yuboradi."))
    notification_to = models.TextField(_("notification email"), blank=True, null=True,
                                       help_text=_("Enter email addresses to notify on submission"))
    success_page_content = models.TextField(
        _("success page content"), blank=True, null=True,
        help_text=_("Muvaffaqiyatli sahifasi shu yerda o‘zgartirishingiz mumkin. HTML sintaksisi qo‘llab-quvvatlanadi")
    )

    class Meta:
        verbose_name = _("survey")
        verbose_name_plural = _("Surveys")
        ordering = ['created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.slug:
            self.slug = generate_unique_slug(Survey, self.slug, self.id)
        else:
            self.slug = generate_unique_slug(Survey, self.name, self.id)
        super().save(*args, **kwargs)


class Section(BaseModel):
    """
    Represents a section/page in a multi-step survey.
    
    Sections allow surveys to be broken down into logical groupings of questions,
    providing better user experience for long surveys with pagination and progress tracking.
    
    Attributes:
        survey (ForeignKey): The survey this section belongs to
        name (CharField): Display name for the section (shown to users)
        description (TextField): Optional description/instructions for the section
        ordering (PositiveIntegerField): Order of this section within the survey (0-indexed)
        
    Meta:
        unique_together: Ensures no duplicate orderings within the same survey
        ordering: Sections ordered by survey then ordering field
        
    Usage:
        Sections are created in the admin interface and questions are assigned to them.
        If no sections exist for a survey, all questions are shown on one page (backward compatible).
        
    Related:
        - Questions: Each question can be assigned to a section via Question.section
        - BranchRule: Rules can be defined to skip to different sections based on answers
        - DraftResponse: Tracks which section user is currently on for save/resume functionality
    """
    survey = models.ForeignKey(Survey, related_name='sections', on_delete=models.CASCADE, verbose_name=_("survey"))
    name = models.CharField(_("name"), max_length=255)
    description = models.TextField(_("description"), blank=True, default='')
    ordering = models.PositiveIntegerField(_("ordering"), default=0)

    class Meta:
        verbose_name = _("section")
        verbose_name_plural = _("Sections")
        ordering = ['survey', 'ordering']
        unique_together = ['survey', 'ordering']

    def __str__(self):
        return f"{self.survey.name} - {self.name}"


class Question(BaseModel):
    type_field = models.PositiveSmallIntegerField(_("field type"), choices=TYPE_FIELD_CHOICES)

    key = models.CharField(
        _("key"), max_length=225, unique=True, null=True, blank=True,
        help_text=_("Noyob kalit savol matnidan avtomatik yaratiladi. Yaratishni istasangiz, bo‘sh joyni to‘ldiring.")
    )
    survey = models.ForeignKey(Survey, related_name='questions', on_delete=models.CASCADE, verbose_name=_("survey"))
    section = models.ForeignKey(Section, related_name='questions', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("section"))
    label = models.CharField(_("label"), max_length=500, help_text=_("Enter your question here."))
    choices = models.TextField(
        _("choices"),
        blank=True, null=True,
        help_text=_(
            "Agar maydon turi radio, tanlanadigan yoki ko‘p variantli bo‘lsa, ajratilgan variantlarni to‘ldiring"
            "vergullar bilan. Masalan: Erkak, Ayol")
    )
    help_text = models.CharField(
        _("help text"),
        max_length=200, blank=True, null=True,
        help_text=_("You can enter help text here.")
    )
    required = models.BooleanField(_("required"), default=True,
                                   help_text=_("Agar belgi qo‘yilsa, foydalanuvchi ushbu savolga javob berishi kerak."))
    ordering = models.PositiveIntegerField(_("ordering"), default=0,
                                           help_text=_("So‘rovnomalar doirasida savollar tartibini belgilaydi."))

    class Meta:
        verbose_name = _("question")
        verbose_name_plural = _("Questions")
        ordering = ["ordering"]

    def __str__(self):
        return f"{self.label}-survey-{self.survey.id}"

    def save(self, *args, **kwargs):
        if self.key:
            self.key = generate_unique_slug(Question, self.key, self.id, "key")
        else:
            self.key = generate_unique_slug(Question, self.label, self.id, "key")

        super(Question, self).save(*args, **kwargs)


class UserAnswer(BaseModel):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, verbose_name=_("survey"))
    user = models.ForeignKey(get_user_model(), blank=True, null=True, on_delete=models.CASCADE, verbose_name=_("user"))
    direction = models.ForeignKey(Direction, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = _("user answer")
        verbose_name_plural = _("User Answers")
        ordering = ["-updated_at"]

    def __str__(self):
        return str(self.id)

    def get_user_photo(self):
        profile = getattr(self.user, 'profile', None)
        if profile and profile.image:
            return profile.image.url
        return settings.MEDIA_URL + 'user_image/default.png'


class Answer(BaseModel):
    question = models.ForeignKey(Question, related_name="answers", on_delete=models.CASCADE, null=True, verbose_name=_("question"))
    value = models.TextField(_("value"), help_text=_("Value of the answer provided by the user."))
    file_value = models.FileField(_("file"), upload_to=upload_survey_file, null=True, blank=True)
    user_answer = models.ForeignKey(UserAnswer, on_delete=models.CASCADE, verbose_name=_("user answer"))

    class Meta:
        verbose_name = _("answer")
        verbose_name_plural = _("Answers")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.question}: {self.value}"

    @property
    def get_value(self):
        if self.question.type_field == TYPE_FIELD.file:
            if self.file_value:
                import os
                from django.urls import reverse
                filename = os.path.basename(self.file_value.name)
                download_url = reverse('djf_surveys:download_file', kwargs={'answer_id': self.id})
                return mark_safe(f'<a href="{download_url}" target="_blank" class="text-blue-600 hover:underline">📎 {filename}</a>')
            return _("No file uploaded")
        elif self.question.type_field == TYPE_FIELD.rating:
            if not self.question.choices:  # use 5 as default for backward compatibility
                self.question.choices = 5
            return create_star(active_star=int(self.value) if self.value else 0, num_stars=int(self.question.choices))
        elif self.question.type_field == TYPE_FIELD.url:
            return mark_safe(f'<a href="{self.value}" target="_blank">{self.value}</a>')
        elif self.question.type_field == TYPE_FIELD.radio or self.question.type_field == TYPE_FIELD.select or \
                self.question.type_field == TYPE_FIELD.multi_select:
            return self.value.strip().replace("_", " ").capitalize()
        else:
            return self.value

    @property
    def get_value_for_csv(self):
        if self.question.type_field == TYPE_FIELD.radio or self.question.type_field == TYPE_FIELD.select or \
                self.question.type_field == TYPE_FIELD.multi_select:
            return self.value.strip().replace("_", " ").capitalize()
        else:
            return self.value.strip()


class DraftResponse(BaseModel):
    """
    Stores partial survey responses for save/resume functionality.
    
    Allows users to save their progress and continue a survey later. Supports both
    authenticated users and anonymous users (via session key).
    
    Attributes:
        survey (ForeignKey): The survey being responded to
        user (ForeignKey): Authenticated user (optional, for logged-in users)
        session_key (CharField): Session identifier for anonymous users (optional)
        current_section (ForeignKey): Section user is currently on
        data (JSONField): Dictionary of question_id -> answer_value mappings
        expires_at (DateTimeField): When this draft expires and can be deleted
        
    Business Logic:
        - Either user or session_key must be set (not both)
        - Data stores only non-file answers (files handled separately)
        - Expiration default is 30 days (configurable via SURVEY_DRAFT_EXPIRY_DAYS)
        - On final submission, draft is deleted automatically
        
    Usage:
        Use DraftService class to interact with drafts (don't create directly):
        - DraftService.save_draft() - Create or update draft
        - DraftService.load_draft() - Retrieve draft for user
        - DraftService.delete_draft() - Remove draft
        
    Cleanup:
        Run 'python manage.py cleanup_expired_drafts' periodically (recommended daily cron job)
    """
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, verbose_name=_("survey"))
    user = models.ForeignKey(get_user_model(), blank=True, null=True, on_delete=models.CASCADE, verbose_name=_("user"))
    session_key = models.CharField(_("session key"), max_length=40, null=True, blank=True)
    current_section = models.ForeignKey(Section, null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_("current section"))
    data = models.JSONField(_("data"), default=dict, help_text=_("Draft response data as JSON"))
    expires_at = models.DateTimeField(_("expires at"))

    class Meta:
        verbose_name = _("draft response")
        verbose_name_plural = _("Draft responses")
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=['user', 'survey']),
            models.Index(fields=['session_key', 'survey']),
        ]

    def __str__(self):
        user_label = self.user.username if self.user else f"Anonymous ({self.session_key[:8]})"
        return f"Draft: {user_label} - {self.survey.name}"


class BranchRule(BaseModel):
    """
    Defines conditional navigation logic for multi-section surveys.
    
    Branch rules allow surveys to dynamically route users to different sections based on
    their answers, enabling complex survey flows like skip logic and conditional paths.
    
    Attributes:
        section (ForeignKey): The section this rule applies to (evaluated after completing this section)
        condition_question (ForeignKey): Question whose answer determines the branch
        condition_operator (CharField): Comparison operator (equals, not_equals, contains, in)
        condition_value (TextField): Value to compare against user's answer
        next_section (ForeignKey): Section to navigate to if condition matches (None = end survey)
        priority (PositiveIntegerField): Evaluation order (lower numbers first, first match wins)
        
    Operators:
        - equals: Exact match (case-insensitive)
        - not_equals: Not equal (case-insensitive)
        - contains: Answer contains condition_value as substring
        - in: Answer matches any value in comma-separated condition_value list
        
    Business Logic:
        - Rules evaluated in priority order (ascending)
        - First matching rule determines next section
        - If no rules match, proceeds to next sequential section
        - If next_section is None, survey ends immediately
        
    Validation:
        - Condition question must be from current or previous section (no forward references)
        - Cannot branch to same section (prevents infinite loops)
        - Next section must be from same survey
        
    Usage Example:
        # Skip to section 3 if user answered "Yes" to question 5
        BranchRule(
            section=section1,
            condition_question=question5,
            condition_operator='equals',
            condition_value='Yes',
            next_section=section3,
            priority=0
        )
        
    Related:
        - BranchEvaluator: Service class that evaluates rules against user answers
        - SectionNavigator: Integrates branch logic with navigation
    """
    section = models.ForeignKey(Section, related_name='branch_rules', on_delete=models.CASCADE, verbose_name=_("section"))
    condition_question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name=_("condition question"))
    condition_operator = models.CharField(
        _("operator"),
        max_length=20,
        choices=[
            ('equals', _('Equals')),
            ('not_equals', _('Not Equals')),
            ('contains', _('Contains')),
            ('in', _('In (comma-separated values)')),
        ]
    )
    condition_value = models.TextField(_("condition value"))
    next_section = models.ForeignKey(
        Section,
        related_name='branch_targets',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("next section"),
        help_text=_("Leave empty to end survey")
    )
    priority = models.PositiveIntegerField(_("priority"), default=0, help_text=_("Lower numbers are evaluated first"))

    class Meta:
        verbose_name = _("branch rule")
        verbose_name_plural = _("Branch rules")
        ordering = ['section', 'priority']

    def __str__(self):
        return f"Rule: {self.section.name} - {self.condition_question.label[:30]}"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        errors = {}
        
        # Validate: condition question must be in current or previous sections
        if self.condition_question and self.section:
            question_section = self.condition_question.section
            if question_section:
                if question_section.survey != self.section.survey:
                    errors['condition_question'] = _("Question must be from the same survey")
                elif question_section.ordering > self.section.ordering:
                    errors['condition_question'] = _("Question must be from current or previous section")
        
        # Validate: prevent branching to same section (infinite loop)
        if self.next_section and self.section and self.next_section.id == self.section.id:
            errors['next_section'] = _("Cannot branch to same section (would create infinite loop)")
        
        # Validate: next_section must be from same survey
        if self.next_section and self.section:
            if self.next_section.survey != self.section.survey:
                errors['next_section'] = _("Target section must be from the same survey")
        
        # Validate condition value format based on question type
        if self.condition_question and self.condition_value:
            question = self.condition_question
            value = self.condition_value
            
            if question.type_field == TYPE_FIELD.number:
                try:
                    float(value)
                except ValueError:
                    errors['condition_value'] = _("Value must be numeric for number field")
            
            elif question.type_field == TYPE_FIELD.date:
                from django.utils.dateparse import parse_date
                if not parse_date(value):
                    errors['condition_value'] = _("Value must be valid date (YYYY-MM-DD)")
            
            elif question.type_field in [TYPE_FIELD.radio, TYPE_FIELD.select]:
                if question.choices:
                    valid_choices = [c.strip().lower() for c in question.choices.split(',')]
                    if value.strip().lower() not in valid_choices:
                        errors['condition_value'] = _(
                            f"Value must be one of: {question.choices}"
                        )
        
        if errors:
            raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    @staticmethod
    def detect_circular_references(survey) -> list:
        """
        Detect circular references in branch rules for a survey.
        
        Returns:
            List of tuples (section, circular_path) if cycles found, empty list otherwise
        """
        from collections import defaultdict, deque
        
        # Build adjacency list
        graph = defaultdict(list)
        sections = Section.objects.filter(survey=survey).prefetch_related('branch_rules')
        
        for section in sections:
            for rule in section.branch_rules.all():
                if rule.next_section:
                    graph[section.id].append(rule.next_section.id)
        
        # Detect cycles using DFS
        def has_cycle(node, visited, rec_stack, path):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor, visited, rec_stack, path):
                        return True
                elif neighbor in rec_stack:
                    # Cycle detected
                    cycle_start = path.index(neighbor)
                    return path[cycle_start:]
            
            path.pop()
            rec_stack.remove(node)
            return False
        
        cycles = []
        visited = set()
        
        for section in sections:
            if section.id not in visited:
                rec_stack = set()
                path = []
                cycle = has_cycle(section.id, visited, rec_stack, path)
                if cycle:
                    cycles.append((section, cycle))
        
        return cycles


class Question2(BaseModel):
    # Type field set for rating questions only
    type_field = models.PositiveSmallIntegerField(
        _("type of input field"), choices=[(TYPE_FIELD.rating, _("Rating"))], default=TYPE_FIELD.rating
    )
    key = models.CharField(
        _("key"), max_length=225, unique=True, null=True, blank=True,
        help_text=_("Noyob kalit savol matnidan avtomatik yaratiladi. Yaratishni istasangiz, bo‘sh joyni to‘ldiring.")
    )
    survey = models.ForeignKey(Survey, related_name='questions2', on_delete=models.CASCADE, verbose_name=_("survey"))
    label = models.CharField(_("yorliq"), max_length=500, help_text=_("Enter your question here."))
    choices = models.TextField(
        _("choices"),
        blank=True, null=True,
        help_text=_("Number of stars in the rating, for example: 5")
    )
    help_text = models.CharField(
        _("help text"),
        max_length=200, blank=True, null=True,
        help_text=_("You can enter help text here.")
    )
    required = models.BooleanField(_("required"), default=True,
                                   help_text=_("Agar belgi qo‘yilsa, foydalanuvchi ushbu savolga javob berishi kerak."))
    ordering = models.PositiveIntegerField(_("ordering"), default=0,
                                           help_text=_("So‘rovnomalar doirasida savollar tartibini belgilaydi."))

    class Meta:
        verbose_name = _("rating question")
        verbose_name_plural = _("Rating Questions")
        ordering = ["ordering"]

    def __str__(self):
        return f"{self.label}-survey-{self.survey.id}"

    def save(self, *args, **kwargs):
        if self.key:
            self.key = generate_unique_slug(Question2, self.key, self.id, "key")
        else:
            self.key = generate_unique_slug(Question2, self.label, self.id, "key")
        super(Question2, self).save(*args, **kwargs)


class UserAnswer2(BaseModel):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, verbose_name=_("survey"))
    user = models.ForeignKey(
        get_user_model(),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="rating_user",
        verbose_name=_("rating user")
    )

    direction = models.ForeignKey(Direction, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = _("user answer for Question2")
        verbose_name_plural = _("User Rating Answers")
        ordering = ["-updated_at"]

    def __str__(self):
        return f"UserAnswer2-{self.id}: {self.user} rated multiple users"


class UserRating(BaseModel):
    user_answer = models.ForeignKey(UserAnswer2, on_delete=models.CASCADE, verbose_name=_("user answer2"))
    rated_user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name=_("rated user"))

    class Meta:
        verbose_name = _("user rating")
        verbose_name_plural = _("Teacher Ratings")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Teacher Rating-{self.id}: {self.user_answer.user} rated {self.rated_user}"


class Answer2(BaseModel):
    question = models.ForeignKey(Question2, related_name="answers2", on_delete=models.CASCADE, verbose_name=_("question2"))
    value = models.PositiveIntegerField(_("value"), help_text=_("Reyting qiymati, masalan, 1 dan 5 gacha."))  # Reyting qiymat uchun moslashtirilgan
    user_rating = models.ForeignKey(UserRating, on_delete=models.CASCADE, verbose_name=_("user rating"))

    class Meta:
        verbose_name = _("answer for Question2")
        verbose_name_plural = _("Rating Answers")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.question}: {self.value} (Rated user: {self.user_rating.rated_user})"


# Signal handlers for file cleanup
from django.db.models.signals import post_delete
from django.dispatch import receiver


@receiver(post_delete, sender=Answer)
def delete_answer_file(sender, instance, **kwargs):
    """
    Delete file from filesystem when Answer is deleted.
    """
    if instance.file_value:
        import os
        try:
            if os.path.isfile(instance.file_value.path):
                os.remove(instance.file_value.path)
        except Exception:
            pass

