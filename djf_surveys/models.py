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
    """
    Generate upload path for survey files with intelligent organization.
    
    File naming format:
    - By Response: survey_{survey_id}/response_{response_id}/Q{question_id}_{timestamp}_{original_filename}
    - By Question: survey_{survey_id}/question_{question_id}/R{response_id}_{timestamp}_{original_filename}
    
    This ensures:
    - Easy identification of which response/question the file belongs to
    - No filename conflicts
    - Traceable mapping to database records
    - Clean folder structure
    """
    import os
    from django.utils.text import get_valid_filename
    from datetime import datetime
    
    # Get related objects
    user_answer = instance.user_answer
    survey = user_answer.survey
    question = instance.question
    
    # Clean the original filename
    original_name, ext = os.path.splitext(filename)
    clean_name = get_valid_filename(original_name)[:50]  # Limit length
    
    # Generate timestamp for uniqueness
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Get file organization preference
    org_type = getattr(survey, 'file_organization', 'response')
    
    if org_type == 'question':
        # Organize by question: survey_{id}/question_{q_id}/R{response_id}_{timestamp}_{filename}
        new_filename = f"R{user_answer.id}_{timestamp}_{clean_name}{ext}"
        path = f'survey_{survey.id}/question_{question.id}/{new_filename}'
    else:
        # Organize by response (default): survey_{id}/response_{r_id}/Q{question_id}_{timestamp}_{filename}
        new_filename = f"Q{question.id}_{timestamp}_{clean_name}{ext}"
        path = f'survey_{survey.id}/response_{user_answer.id}/{new_filename}'
    
    return path


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
    description = models.TextField(_("description"), default='')
    slug = models.SlugField(_("slug"), max_length=225, default='')
    editable = models.BooleanField(_("editable"), default=True,
                                   help_text=_("If unchecked, users cannot edit their submissions."))
    deletable = models.BooleanField(_("deletable"), default=True,
                                    help_text=_("If unchecked, users cannot delete their submissions."))
    duplicate_entry = models.BooleanField(_("allow multiple submissions"), default=False,
                                          help_text=_("If checked, users can submit multiple responses."))
    private_response = models.BooleanField(_("private response"), default=False,
                                           help_text=_("If checked, only administrators and owners can access responses."))
    can_anonymous_user = models.BooleanField(_("allow anonymous submissions"), default=False,
                                             help_text=_("If checked, unauthenticated users can submit responses."))
    notification_to = models.TextField(_("notification email"), blank=True, null=True,
                                       help_text=_("Enter email addresses to notify on submission"))
    success_page_content = models.TextField(
        _("success page content"), blank=True, null=True,
        help_text=_("You can customize the success page here. HTML syntax is supported.")
    )
    
    # File organization settings
    FILE_ORG_BY_RESPONSE = 'response'
    FILE_ORG_BY_QUESTION = 'question'
    FILE_ORGANIZATION_CHOICES = [
        (FILE_ORG_BY_RESPONSE, _('By Response (One folder per submission)')),
        (FILE_ORG_BY_QUESTION, _('By Question (One folder per question)')),
    ]
    
    file_organization = models.CharField(
        _("file organization"),
        max_length=20,
        choices=FILE_ORGANIZATION_CHOICES,
        default=FILE_ORG_BY_RESPONSE,
        help_text=_("Choose how to organize uploaded files: by response or by question")
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
    
    def get_absolute_url(self):
        """Get the full URL for this survey."""
        from django.urls import reverse
        return reverse('djf_surveys:detail', kwargs={'slug': self.slug})
    
    def generate_qr_code(self, request=None):
        """
        Generate QR code for survey URL.
        Returns base64 encoded image data.
        """
        import qrcode
        import io
        import base64
        from django.urls import reverse
        
        # Get full URL
        if request:
            survey_url = request.build_absolute_uri(self.get_absolute_url())
        else:
            # Fallback to relative URL if no request
            survey_url = self.get_absolute_url()
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(survey_url)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_base64}"
    
    def get_qr_download_url(self):
        """Get URL to download QR code."""
        from django.urls import reverse
        return reverse('djf_surveys:survey_qr_download', kwargs={'slug': self.slug})
    
    def get_upload_folder_path(self):
        """Get the base folder path for this survey's uploads."""
        return f'survey_{self.id}'
    
    def get_all_uploaded_files(self):
        """
        Get all uploaded files for this survey.
        
        Returns:
            QuerySet of Answer objects that have file uploads
        """
        from djf_surveys.models import Answer, TYPE_FIELD
        return Answer.objects.filter(
            user_answer__survey=self,
            question__type_field=TYPE_FIELD.file,
            file_value__isnull=False
        ).exclude(file_value='').select_related('user_answer', 'question')
    
    def get_file_statistics(self):
        """
        Get statistics about uploaded files.
        
        Returns:
            dict with file count, total size, organization type
        """
        import os
        from django.conf import settings
        
        files = self.get_all_uploaded_files()
        total_size = 0
        file_count = files.count()
        
        for answer in files:
            if answer.file_value:
                try:
                    file_path = os.path.join(settings.MEDIA_ROOT, answer.file_value.name)
                    if os.path.exists(file_path):
                        total_size += os.path.getsize(file_path)
                except:
                    pass
        
        # Convert bytes to human readable
        size_mb = total_size / (1024 * 1024)
        
        return {
            'file_count': file_count,
            'total_size_bytes': total_size,
            'total_size_mb': round(size_mb, 2),
            'organization_type': self.file_organization,
            'base_folder': self.get_upload_folder_path(),
        }


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
        help_text=_("Unique key automatically generated from question text. Leave blank to auto-generate.")
    )
    survey = models.ForeignKey(Survey, related_name='questions', on_delete=models.CASCADE, verbose_name=_("survey"))
    section = models.ForeignKey(Section, related_name='questions', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("section"))
    label = models.CharField(_("label"), max_length=500, help_text=_("Enter your question here."))
    choices = models.TextField(
        _("choices"),
        blank=True, null=True,
        help_text=_(
            "If field type is radio, select, or multi-select, enter options separated by"
            "commas. Example: Male, Female")
    )
    help_text = models.CharField(
        _("help text"),
        max_length=200, blank=True, null=True,
        help_text=_("You can enter help text here.")
    )
    required = models.BooleanField(_("required"), default=True,
                                   help_text=_("If checked, users must answer this question."))
    ordering = models.PositiveIntegerField(_("ordering"), default=0,
                                           help_text=_("Determines the order of questions within the survey."))
    enable_branching = models.BooleanField(_("enable branching"), default=False,
                                           help_text=_("Enable section branching for this question (radio type only)"))
    branch_config = models.JSONField(_("branch configuration"), default=dict, blank=True,
                                     help_text=_("Maps each choice to target section ID"))
    
    # Validation fields
    min_length = models.PositiveIntegerField(
        _("minimum length"), 
        null=True, 
        blank=True,
        help_text=_("Minimum number of characters required (for text fields). Leave blank for no minimum.")
    )
    max_length = models.PositiveIntegerField(
        _("maximum length"), 
        null=True, 
        blank=True,
        help_text=_("Maximum number of characters allowed (for text fields). Leave blank for default maximum.")
    )
    regex_pattern = models.CharField(
        _("regex pattern"),
        max_length=500,
        null=True,
        blank=True,
        help_text=_("Regular expression pattern for validation (e.g., ^[A-Z0-9]+$ for alphanumeric). Leave blank for no pattern matching.")
    )
    validation_message = models.CharField(
        _("validation message"),
        max_length=200,
        null=True,
        blank=True,
        help_text=_("Custom error message to display when validation fails. Leave blank for default message.")
    )

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
    
    def get_branch_target(self, option_value):
        """
        Get target section ID for a given choice value.
        
        Args:
            option_value: The choice value selected by user
            
        Returns:
            Section ID to navigate to, or None if no branching configured
        """
        if not self.enable_branching or not self.branch_config:
            return None
        
        # Normalize the option value for comparison - must match save logic
        from djf_surveys.utils_normalize import normalize_choice_key
        normalized_value = normalize_choice_key(str(option_value))
        
        # Check direct match first
        if normalized_value in self.branch_config:
            return self.branch_config[normalized_value]
        
        # Check with original value
        if option_value in self.branch_config:
            return self.branch_config[option_value]
        
        return None
    
    def set_branch_target(self, option_value, section_id):
        """
        Set target section for a given choice value.
        
        Args:
            option_value: The choice value
            section_id: Target section ID (or None to end survey)
        """
        if not self.branch_config:
            self.branch_config = {}
        
        normalized_value = str(option_value).strip().lower().replace(' ', '_')
        self.branch_config[normalized_value] = section_id
    
    @property
    def has_branching_configured(self):
        """Check if branching is enabled and configured."""
        return self.enable_branching and bool(self.branch_config)
    
    def get_validation_defaults(self):
        """
        Get default validation values based on field type.
        
        Returns:
            dict: Dictionary with min_length, max_length, and regex_pattern defaults
        """
        defaults = {
            TYPE_FIELD.text: {'min_length': 0, 'max_length': 500, 'regex_pattern': None},
            TYPE_FIELD.text_area: {'min_length': 0, 'max_length': 5000, 'regex_pattern': None},
            TYPE_FIELD.number: {'min_length': None, 'max_length': None, 'regex_pattern': r'^\d+$'},
            TYPE_FIELD.url: {'min_length': 0, 'max_length': 2048, 'regex_pattern': r'^https?://.*'},
            TYPE_FIELD.email: {'min_length': 0, 'max_length': 254, 'regex_pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'},
            TYPE_FIELD.radio: {'min_length': None, 'max_length': None, 'regex_pattern': None},
            TYPE_FIELD.select: {'min_length': None, 'max_length': None, 'regex_pattern': None},
            TYPE_FIELD.multi_select: {'min_length': None, 'max_length': None, 'regex_pattern': None},
            TYPE_FIELD.date: {'min_length': None, 'max_length': None, 'regex_pattern': r'^\d{4}-\d{2}-\d{2}$'},
            TYPE_FIELD.rating: {'min_length': None, 'max_length': None, 'regex_pattern': None},
            TYPE_FIELD.file: {'min_length': None, 'max_length': None, 'regex_pattern': None},
        }
        return defaults.get(self.type_field, {'min_length': None, 'max_length': None, 'regex_pattern': None})
    
    def get_effective_min_length(self):
        """Get effective minimum length (custom or default)."""
        if self.min_length is not None:
            return self.min_length
        return self.get_validation_defaults().get('min_length')
    
    def get_effective_max_length(self):
        """Get effective maximum length (custom or default)."""
        if self.max_length is not None:
            return self.max_length
        return self.get_validation_defaults().get('max_length')
    
    def get_effective_regex_pattern(self):
        """Get effective regex pattern (custom or default)."""
        if self.regex_pattern:
            return self.regex_pattern
        return self.get_validation_defaults().get('regex_pattern')
    
    def validate_answer(self, value):
        """
        Validate an answer value against this question's validation rules.
        
        Args:
            value: The answer value to validate
            
        Returns:
            tuple: (is_valid: bool, error_message: str or None)
        """
        import re
        
        # Skip validation for non-text fields that don't support it
        if self.type_field in [TYPE_FIELD.radio, TYPE_FIELD.select, TYPE_FIELD.multi_select, 
                              TYPE_FIELD.rating, TYPE_FIELD.file]:
            return True, None
        
        # Convert to string for validation
        value_str = str(value) if value is not None else ''
        
        # Check minimum length
        min_len = self.get_effective_min_length()
        if min_len is not None and len(value_str) < min_len:
            if self.validation_message:
                return False, self.validation_message
            return False, f"Minimum {min_len} characters required"
        
        # Check maximum length
        max_len = self.get_effective_max_length()
        if max_len is not None and len(value_str) > max_len:
            if self.validation_message:
                return False, self.validation_message
            return False, f"Maximum {max_len} characters allowed"
        
        # Check regex pattern
        pattern = self.get_effective_regex_pattern()
        if pattern and value_str:
            try:
                if not re.match(pattern, value_str):
                    if self.validation_message:
                        return False, self.validation_message
                    return False, "Invalid format"
            except re.error:
                # Invalid regex pattern
                return True, None
        
        return True, None
    
    def get_validation_rules_dict(self):
        """
        Get validation rules as a dictionary for frontend use.
        
        Returns:
            dict: Validation rules including defaults
        """
        return {
            'min_length': self.get_effective_min_length(),
            'max_length': self.get_effective_max_length(),
            'regex_pattern': self.get_effective_regex_pattern(),
            'validation_message': self.validation_message or 'Invalid input',
            'required': self.required,
        }


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
    file_url = models.URLField(_("file URL"), max_length=500, blank=True, null=True, help_text=_("Accessible URL for uploaded file"))
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

    def get_file_url(self, request=None):
        """
        Get accessible URL for file upload.
        
        Returns file_url if available, otherwise generates from file_value.
        For CSV exports, this ensures a clickable URL is always available.
        """
        if self.file_url:
            return self.file_url
        
        if self.file_value:
            if request:
                from django.urls import reverse
                download_url = reverse('djf_surveys:download_file', kwargs={'answer_id': self.id})
                return request.build_absolute_uri(download_url)
            else:
                import os
                return self.file_value.url if self.file_value else ""
        
        return ""
    
    @property
    def get_value_for_csv(self):
        """Get value formatted for CSV export."""
        if self.question.type_field == TYPE_FIELD.file:
            # Return the accessible file URL for CSV
            return self.get_file_url()
        elif self.question.type_field == TYPE_FIELD.radio or self.question.type_field == TYPE_FIELD.select or \
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
        help_text=_("Unique key automatically generated from question text. Leave blank to auto-generate.")
    )
    survey = models.ForeignKey(Survey, related_name='questions2', on_delete=models.CASCADE, verbose_name=_("survey"))
    label = models.CharField(_("label"), max_length=500, help_text=_("Enter your question here."))
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
                                   help_text=_("If checked, users must answer this question."))
    ordering = models.PositiveIntegerField(_("ordering"), default=0,
                                           help_text=_("Determines the order of questions within the survey."))

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
    value = models.PositiveIntegerField(_("value"), help_text=_("Rating value, for example, from 1 to 5."))  # Adapted for rating value
    user_rating = models.ForeignKey(UserRating, on_delete=models.CASCADE, verbose_name=_("user rating"))

    class Meta:
        verbose_name = _("answer for Question2")
        verbose_name_plural = _("Rating Answers")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.question}: {self.value} (Rated user: {self.user_rating.rated_user})"


class StorageConfiguration(BaseModel):
    """
    Configuration for file storage backend.
    
    Only one configuration can be active at a time.
    Supports local filesystem and Google Drive storage.
    """
    PROVIDER_CHOICES = [
        ('local', 'Local Storage'),
        ('google_drive', 'Google Drive'),
    ]
    
    provider = models.CharField(_("storage provider"), max_length=20, choices=PROVIDER_CHOICES, default='local')
    credentials = models.JSONField(_("credentials"), default=dict, blank=True, help_text=_("Encrypted credentials for cloud storage"))
    config = models.JSONField(_("configuration"), default=dict, blank=True, help_text=_("Additional configuration options"))
    is_active = models.BooleanField(_("is active"), default=False)
    
    class Meta:
        verbose_name = _("storage configuration")
        verbose_name_plural = _("Storage Configurations")
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"{self.get_provider_display()} {'(Active)' if self.is_active else ''}"
    
    def save(self, *args, **kwargs):
        """Ensure only one configuration is active at a time."""
        if self.is_active:
            StorageConfiguration.objects.filter(is_active=True).update(is_active=False)
        super().save(*args, **kwargs)
    
    @classmethod
    def get_active(cls):
        """Get the currently active storage configuration."""
        return cls.objects.filter(is_active=True).first()
    
    def test_connection(self):
        """Test connection to the configured storage provider."""
        from djf_surveys.storage import StorageManager
        manager = StorageManager()
        backend = manager._create_backend(self.provider, self.config, self.credentials)
        return backend.test_connection()


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

