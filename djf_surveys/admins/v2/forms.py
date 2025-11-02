from django import forms
from django.utils.translation import gettext_lazy as _
from djf_surveys.models import Question, Survey
from djf_surveys.widgets import InlineChoiceField


class QuestionForm(forms.ModelForm):
    section = forms.ModelChoiceField(
        queryset=None,
        required=False,
        label=_("Section"),
        help_text=_("Select a section for this question")
    )
    
    class Meta:
        model = Question
        fields = ['label', 'key', 'help_text', 'required', 'section', 
                 'min_length', 'max_length', 'regex_pattern', 'validation_message']
    
    def __init__(self, *args, **kwargs):
        survey = kwargs.pop('survey', None)
        super().__init__(*args, **kwargs)
        from djf_surveys.models import Section
        if survey:
            self.fields['section'].queryset = Section.objects.filter(survey=survey).order_by('ordering')
        else:
            self.fields['section'].queryset = Section.objects.none()


class QuestionWithChoicesForm(forms.ModelForm):
    section = forms.ModelChoiceField(
        queryset=None,
        required=False,
        label=_("Section"),
        help_text=_("Select a section for this question")
    )
    
    enable_branching = forms.BooleanField(
        required=False,
        label=_("Enable Section Branching"),
        help_text=_("Route users to different sections based on their answer (radio questions only)")
    )
    
    class Meta:
        model = Question
        fields = ['label', 'key', 'choices', 'help_text', 'required', 'section', 'enable_branching',
                 'min_length', 'max_length', 'regex_pattern', 'validation_message']
    
    def __init__(self, *args, **kwargs):
        survey = kwargs.pop('survey', None)
        super().__init__(*args, **kwargs)
        self.fields['choices'].widget = InlineChoiceField()
        self.fields['choices'].help_text = _("Yana variant qo'shish uchun + tugmasini bosing")
        from djf_surveys.models import Section
        if survey:
            self.fields['section'].queryset = Section.objects.filter(survey=survey).order_by('ordering')
        else:
            self.fields['section'].queryset = Section.objects.none()


class QuestionFormRatings(forms.ModelForm):
    section = forms.ModelChoiceField(
        queryset=None,
        required=False,
        label=_("Section"),
        help_text=_("Select a section for this question")
    )
    
    class Meta:
        model = Question
        fields = ['label', 'key', 'choices', 'help_text', 'required', 'section']
    
    def __init__(self, *args, **kwargs):
        survey = kwargs.pop('survey', None)
        super().__init__(*args, **kwargs)
        self.fields['choices'].widget = forms.NumberInput(attrs={'max': 10, 'min': 1})
        self.fields['choices'].help_text = _("1 va 10 orasida bo'lishi kerak")
        self.fields['choices'].label = _("Reytinglar soni")
        self.fields['choices'].initial = 5
        from djf_surveys.models import Section
        if survey:
            self.fields['section'].queryset = Section.objects.filter(survey=survey).order_by('ordering')
        else:
            self.fields['section'].queryset = Section.objects.none()


class SurveyForm(forms.ModelForm):
    
    class Meta:
        model = Survey
        fields = [
            'name', 'description', 'editable', 'deletable', 
            'duplicate_entry', 'private_response', 'can_anonymous_user',
            'notification_to', 'success_page_content', 'file_organization'
        ]
        widgets = {
            'file_organization': forms.RadioSelect(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['notification_to'].widget = InlineChoiceField()
