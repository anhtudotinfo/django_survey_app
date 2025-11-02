from django.utils.text import capfirst
from django.utils.translation import gettext, gettext_lazy as _
from django.views.generic.edit import CreateView, UpdateView
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.http import Http404
from djf_surveys.app_settings import SURVEYS_ADMIN_BASE_PATH
from djf_surveys.models import Survey, Question, TYPE_FIELD, TYPE_FIELD_CHOICES
from djf_surveys.mixin import ContextTitleMixin
from djf_surveys.admins.v2.forms import QuestionForm, QuestionWithChoicesForm, QuestionFormRatings


@method_decorator(staff_member_required, name='dispatch')
class AdminCreateQuestionView(ContextTitleMixin, CreateView):
    template_name = 'djf_surveys/admins/question_form_v2.html'
    success_url = reverse_lazy("djf_surveys:")
    title_page = _("Savol kiritish")
    survey = None
    type_field_id = None

    def dispatch(self, request, *args, **kwargs):
        self.survey = get_object_or_404(Survey, id=kwargs['pk'])
        self.type_field_id = kwargs['type_field']
        if self.type_field_id not in TYPE_FIELD:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_form_class(self):
        choices = [TYPE_FIELD.multi_select, TYPE_FIELD.select, TYPE_FIELD.radio]
        if self.type_field_id in choices:
            return QuestionWithChoicesForm
        elif self.type_field_id == TYPE_FIELD.rating:
            return QuestionFormRatings
        else:
            return QuestionForm

    def post(self, request, *args, **kwargs):
        self.object = None  # Required for CreateView
        form = self.get_form()
        if form.is_valid():
            question = form.save(commit=False)
            question.survey = self.survey
            question.type_field = self.type_field_id
            
            # Handle branching configuration for radio questions
            if self.type_field_id == TYPE_FIELD.radio and form.cleaned_data.get('enable_branching'):
                branch_config = {}
                choices = form.cleaned_data.get('choices', '').split(',') if isinstance(form.cleaned_data.get('choices', ''), str) else []
                
                for choice in choices:
                    if choice.strip():
                        # Normalize choice for key (lowercase, replace spaces with underscores)
                        choice_key = choice.strip().lower().replace(' ', '_')
                        target_field = f'branch_target_{choice_key}'
                        target = request.POST.get(target_field)
                        
                        if target:
                            try:
                                branch_config[choice_key] = int(target) if target != '' else None
                            except (ValueError, TypeError):
                                pass
                
                question.branch_config = branch_config
            
            question.save()
            self.object = question  # Set after save
            messages.success(self.request, gettext("%(page_action_name)s succeeded.") % dict(
                page_action_name=capfirst(self.title_page.lower())))
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type_field_id'] = self.type_field_id
        # Add sections for branching configuration
        from djf_surveys.models import Section
        import json
        sections = Section.objects.filter(survey=self.survey).order_by('ordering')
        context['sections'] = json.dumps([{'id': s.id, 'name': s.name} for s in sections])
        return context

    def get_success_url(self):
        return reverse("djf_surveys:admin_forms_survey", args=[self.survey.slug])

    def get_sub_title_page(self):
        return gettext("Type Field %s") % dict(TYPE_FIELD_CHOICES).get(self.type_field_id, "Unknown")


@method_decorator(staff_member_required, name='dispatch')
class AdminUpdateQuestionView(ContextTitleMixin, UpdateView):
    model = Question
    template_name = 'djf_surveys/admins/question_form_v2.html'
    success_url = SURVEYS_ADMIN_BASE_PATH
    title_page = _("Edit question")
    survey = None
    type_field_id = None

    def dispatch(self, request, *args, **kwargs):
        question = self.get_object()
        self.type_field_id = question.type_field
        self.survey = question.survey
        return super().dispatch(request, *args, **kwargs)

    def get_form_class(self):
        choices = [TYPE_FIELD.multi_select, TYPE_FIELD.select, TYPE_FIELD.radio]
        if self.type_field_id in choices:
            return QuestionWithChoicesForm
        elif self.type_field_id == TYPE_FIELD.rating:
            return QuestionFormRatings
        else:
            return QuestionForm
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['survey'] = self.survey
        return kwargs

    def get_object(self):
        object = super(UpdateView, self).get_object(self.get_queryset())
        if object.type_field == TYPE_FIELD.rating:
            if not object.choices:  # use 5 as default for backward compatibility
                object.choices = 5
        return object

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            question = form.save(commit=False)
            
            # Handle branching configuration for radio questions
            if self.type_field_id == TYPE_FIELD.radio and form.cleaned_data.get('enable_branching'):
                from djf_surveys.utils_normalize import normalize_choice_key
                
                branch_config = {}
                choices = form.cleaned_data.get('choices', '').split(',') if isinstance(form.cleaned_data.get('choices', ''), str) else []
                
                print(f"DEBUG: Processing branching for {len(choices)} choices")  # Debug
                
                for choice in choices:
                    if choice.strip():
                        # Normalize choice for key - must match JavaScript normalization
                        choice_key = normalize_choice_key(choice)
                        target_field = f'branch_target_{choice_key}'
                        target = request.POST.get(target_field)
                        
                        print(f"DEBUG: Choice '{choice}' -> key '{choice_key}' -> field '{target_field}' -> value '{target}'")  # Debug
                        
                        if target and target != '':
                            try:
                                branch_config[choice_key] = int(target)
                                print(f"DEBUG: Saved {choice_key} = {target}")  # Debug
                            except (ValueError, TypeError) as e:
                                print(f"DEBUG: Error converting {target}: {e}")  # Debug
                                pass
                
                print(f"DEBUG: Final branch_config: {branch_config}")  # Debug
                question.branch_config = branch_config
            else:
                # Clear branching if disabled
                question.enable_branching = False
                question.branch_config = {}
            
            question.save()
            messages.success(self.request, gettext("Question updated successfully."))
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type_field_id'] = self.type_field_id
        # Add sections for branching configuration
        from djf_surveys.models import Section
        import json
        sections = Section.objects.filter(survey=self.survey).order_by('ordering')
        context['sections'] = json.dumps([{'id': s.id, 'name': s.name} for s in sections])
        # Add current question's branch config for pre-populating the form
        question = self.get_object()
        context['current_branch_config'] = json.dumps(question.branch_config if question.enable_branching else {})
        return context

    def get_success_url(self):
        return reverse("djf_surveys:admin_forms_survey", args=[self.survey.slug])

    def get_sub_title_page(self):
        question = self.get_object()
        return gettext("Type Field %s") % question.get_type_field_display()
