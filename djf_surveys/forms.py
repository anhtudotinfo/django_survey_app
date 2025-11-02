from typing import List, Tuple, Optional
from django import forms
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import transaction
from django.core.validators import MaxLengthValidator, MinLengthValidator, RegexValidator
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from accounts.models import Profile
from djf_surveys.models import (
    Answer, TYPE_FIELD, UserAnswer, Question, Direction, Question2,
    UserAnswer2, UserRating, Answer2, Section
)
from djf_surveys.widgets import CheckboxSelectMultipleSurvey, RadioSelectSurvey, DateSurvey, RatingSurvey
from djf_surveys.app_settings import DATE_INPUT_FORMAT, SURVEY_FIELD_VALIDATORS
from djf_surveys.validators import RatingValidator, FileTypeValidator, FileSizeValidator
import re


def make_choices(question: Question) -> List[Tuple[str, str]]:
    choices = []
    for choice in question.choices.split(','):
        choice = choice.strip()
        choices.append((choice.replace(' ', '_').lower(), choice))
    return choices


class BaseSurveyForm(forms.Form):

    def __init__(self, survey, user, current_section: Optional[Section] = None, *args, **kwargs):
        self.survey = survey
        self.user = user if (user and hasattr(user, 'is_authenticated') and user.is_authenticated) else None
        self.current_section = current_section
        self.field_names = []
        
        # Get questions for current section or all questions if no section
        if current_section:
            self.questions = current_section.questions.all().order_by('ordering')
        else:
            self.questions = self.survey.questions.all().order_by('ordering')
        
        super().__init__(*args, **kwargs)

        for question in self.questions:
            # to generate field name
            field_name = f'field_survey_{question.id}'

            if question.type_field == TYPE_FIELD.multi_select:
                choices = make_choices(question)
                self.fields[field_name] = forms.MultipleChoiceField(
                    choices=choices, label=question.label,
                    widget=CheckboxSelectMultipleSurvey,
                )
            elif question.type_field == TYPE_FIELD.radio:
                choices = make_choices(question)
                self.fields[field_name] = forms.ChoiceField(
                    choices=choices, label=question.label,
                    widget=RadioSelectSurvey
                )
            elif question.type_field == TYPE_FIELD.select:
                choices = make_choices(question)
                empty_choice = [("", _("Select"))]
                choices = empty_choice + choices
                self.fields[field_name] = forms.ChoiceField(
                    choices=choices, label=question.label
                )
            elif question.type_field == TYPE_FIELD.number:
                validators = []
                regex = question.get_effective_regex_pattern()
                if regex:
                    try:
                        validators.append(RegexValidator(
                            regex=regex,
                            message=question.validation_message or _("Invalid number format")
                        ))
                    except re.error:
                        pass
                self.fields[field_name] = forms.IntegerField(
                    label=question.label,
                    validators=validators
                )
            elif question.type_field == TYPE_FIELD.url:
                validators = []
                max_len = question.get_effective_max_length()
                if max_len:
                    validators.append(MaxLengthValidator(max_len))
                
                regex = question.get_effective_regex_pattern()
                if regex:
                    try:
                        validators.append(RegexValidator(
                            regex=regex,
                            message=question.validation_message or _("Invalid URL format")
                        ))
                    except re.error:
                        pass
                
                self.fields[field_name] = forms.URLField(
                    label=question.label,
                    validators=validators,
                    max_length=max_len if max_len else None
                )
            elif question.type_field == TYPE_FIELD.email:
                validators = []
                max_len = question.get_effective_max_length()
                if max_len:
                    validators.append(MaxLengthValidator(max_len))
                
                regex = question.get_effective_regex_pattern()
                if regex:
                    try:
                        validators.append(RegexValidator(
                            regex=regex,
                            message=question.validation_message or _("Invalid email format")
                        ))
                    except re.error:
                        pass
                
                self.fields[field_name] = forms.EmailField(
                    label=question.label,
                    validators=validators,
                    max_length=max_len if max_len else None
                )
            elif question.type_field == TYPE_FIELD.date:
                self.fields[field_name] = forms.DateField(
                    label=question.label, widget=DateSurvey(),
                    input_formats=DATE_INPUT_FORMAT
                )
            elif question.type_field == TYPE_FIELD.text_area:
                validators = []
                
                min_len = question.get_effective_min_length()
                if min_len is not None and min_len > 0:
                    validators.append(MinLengthValidator(min_len))
                
                max_len = question.get_effective_max_length()
                if max_len is not None:
                    validators.append(MaxLengthValidator(max_len))
                
                regex = question.get_effective_regex_pattern()
                if regex:
                    try:
                        validators.append(RegexValidator(
                            regex=regex,
                            message=question.validation_message or _("Invalid format")
                        ))
                    except re.error:
                        pass
                
                self.fields[field_name] = forms.CharField(
                    label=question.label, 
                    widget=forms.Textarea,
                    validators=validators,
                    max_length=max_len if max_len else None
                )
            elif question.type_field == TYPE_FIELD.rating:
                if not question.choices:  # use 5 as default for backward compatibility
                    question.choices = 5
                self.fields[field_name] = forms.CharField(
                    label=question.label, widget=RatingSurvey,
                    validators=[MaxLengthValidator(len(str(int(question.choices)))),
                                RatingValidator(int(question.choices))]
                )
                self.fields[field_name].widget.num_ratings = int(question.choices)
            elif question.type_field == TYPE_FIELD.file:
                self.fields[field_name] = forms.FileField(
                    label=question.label,
                    validators=[FileTypeValidator(), FileSizeValidator()]
                )
            else:
                validators = []
                
                # Add min length validator
                min_len = question.get_effective_min_length()
                if min_len is not None and min_len > 0:
                    validators.append(MinLengthValidator(min_len))
                
                # Add max length validator
                max_len = question.get_effective_max_length()
                if max_len is not None:
                    validators.append(MaxLengthValidator(max_len))
                
                # Add regex validator
                regex = question.get_effective_regex_pattern()
                if regex:
                    try:
                        validators.append(RegexValidator(
                            regex=regex,
                            message=question.validation_message or _("Invalid format")
                        ))
                    except re.error:
                        pass  # Skip invalid regex
                
                self.fields[field_name] = forms.CharField(
                    label=question.label,
                    validators=validators,
                    max_length=max_len if max_len else None
                )

            self.fields[field_name].required = question.required
            self.fields[field_name].help_text = question.help_text
            self.field_names.append(field_name)

    def clean(self):
        cleaned_data = super().clean()

        for field_name in self.field_names:
            try:
                field = cleaned_data[field_name]
            except KeyError:
                raise forms.ValidationError("Siz to‘g‘ri ma’lumotlarni kiritishingiz shart")

            if self.fields[field_name].required and not field:
                self.add_error(field_name, 'Bu maydon to‘ldirilishi shart')

        return cleaned_data


class CreateSurveyForm(BaseSurveyForm):
    # Direction field removed - not needed anymore
    pass

    def __init__(self, survey, user, current_section=None, user_answer=None, *args, **kwargs):
        self.survey = survey
        self.user = user
        self.user_answer = user_answer  # Accept existing UserAnswer from view
        super().__init__(survey=survey, user=user, current_section=current_section, *args, **kwargs)

    @transaction.atomic
    def save(self):
        cleaned_data = super().clean()

        # Use existing UserAnswer or create new one
        if self.user_answer:
            user_answer = self.user_answer
            # For multi-section surveys, answers are already saved via update_or_create
            # Don't delete them!
            should_delete_answers = False
        else:
            # Fallback: create new if not provided (shouldn't happen normally)
            user_answer = UserAnswer.objects.create(
                survey=self.survey, user=self.user,
                direction=None
            )
            should_delete_answers = True
        
        # Only delete existing answers for non-section surveys (to prevent duplicates on resubmit)
        if should_delete_answers:
            Answer.objects.filter(user_answer=user_answer).delete()
        
        # Create UserAnswer2 for ratings (always create new for each submission)
        user_answer2 = UserAnswer2.objects.create(
            survey=self.survey, user=self.user,
            direction=None
        )

        # Save general questions
        for question in self.questions:
            field_name = f'field_survey_{question.id}'
            
            if question.type_field == TYPE_FIELD.file:
                # Handle file upload
                file_field = cleaned_data.get(field_name)
                Answer.objects.create(
                    question=question,
                    value='',  # Empty value for file fields
                    file_value=file_field,
                    user_answer=user_answer
                )
            elif question.type_field == TYPE_FIELD.multi_select:
                value = ",".join(cleaned_data[field_name])
                Answer.objects.create(
                    question=question, value=value, user_answer=user_answer
                )
            else:
                value = cleaned_data[field_name]
                Answer.objects.create(
                    question=question, value=value, user_answer=user_answer
                )

        # Reyting savollarni saqlash
        for key, val in self.data.items():
            if key.startswith("rating_") and len(key.split("_")) == 3:
                _, profile_id_str, question_id_str = key.split("_")
                try:
                    rating_value = int(val)
                    profile_id = int(profile_id_str)
                    question_id = int(question_id_str)

                    question = get_object_or_404(Question2, id=question_id)
                    profile_obj = Profile.objects.get(id=profile_id)

                    # Because model 'UserRating.rated_user' -> ForeignKey(User)
                    user_rating = UserRating.objects.create(
                        user_answer=user_answer2,
                        rated_user=profile_obj.user  # <-- .user bilan User obyektini oldik
                    )
                    Answer2.objects.create(
                        question=question,
                        value=rating_value,
                        user_rating=user_rating
                    )
                except (ObjectDoesNotExist, ValueError) as e:
                    print("Xatolik:", e)
                    continue  # Noto‘g‘ri ma’lumotlarni o‘tkazib yuboring

        return user_answer


class EditSurveyForm(BaseSurveyForm):

    def __init__(self, user_answer, *args, **kwargs):
        self.survey = user_answer.survey
        self.user_answer = user_answer
        super().__init__(survey=self.survey, user=user_answer.user, *args, **kwargs)
        self._set_initial_data()

    def _set_initial_data(self):
        answers = self.user_answer.answer_set.all()

        for answer in answers:
            field_name = f'field_survey_{answer.question.id}'
            if field_name not in self.fields:
                continue  # Skip if question not in current section
                
            if answer.question.type_field == TYPE_FIELD.file:
                # For file fields, we can't set initial in the same way
                # Just show filename if exists
                if answer.file_value:
                    self.fields[field_name].help_text = f"Current file: {answer.file_value.name}"
            elif answer.question.type_field == TYPE_FIELD.multi_select:
                self.fields[field_name].initial = answer.value.split(',')
            else:
                self.fields[field_name].initial = answer.value

