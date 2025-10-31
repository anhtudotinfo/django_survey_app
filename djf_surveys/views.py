from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext, gettext_lazy as _
from django.views.generic.list import ListView
from django.views.generic.edit import FormMixin
from django.views.generic.detail import DetailView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.utils.decorators import method_decorator
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.http import Http404, FileResponse, HttpResponseForbidden
import os
from accounts.models import Profile
from djf_surveys.models import (
    Survey, UserAnswer, UserAnswer2, Question, Question2, 
    TYPE_FIELD, Answer2, UserRating, Section
)
from djf_surveys.forms import CreateSurveyForm, EditSurveyForm
from djf_surveys.mixin import ContextTitleMixin
from djf_surveys import app_settings
from djf_surveys.utils import NewPaginator
from djf_surveys.navigation import SectionNavigator
from djf_surveys.draft_service import DraftService


class SurveyListView(ContextTitleMixin, UserPassesTestMixin, ListView):
    model = Survey
    title_page = "So‘rovnomalar ro‘yxati"
    paginate_by = app_settings.SURVEY_PAGINATION_NUMBER['survey_list']
    paginator_class = NewPaginator

    def test_func(self):
        return True

    def get_queryset(self):
        filter = {}
        if app_settings.SURVEY_ANONYMOUS_VIEW_LIST and not self.request.user.is_authenticated:
            filter["can_anonymous_user"] = True
        query = self.request.GET.get('q')
        if query:
            object_list = self.model.objects.filter(name__icontains=query, **filter)
        else:
            object_list = self.model.objects.filter(**filter)
        return object_list

    # def get_template_names(self):
    #     """Open admin page for staff users"""
    #     if self.request.user.is_authenticated and self.request.user.is_staff:
    #         return ["djf_surveys/admins/survey_list.html"]
    #     return ["djf_surveys/survey_list.html"]

    def get_context_data(self, **kwargs):
        page_number = self.request.GET.get('page', 1)
        context = super().get_context_data(**kwargs)
        page_range = context['page_obj'].paginator.get_elided_page_range(number=page_number)
        context['page_range'] = page_range
        return context


class SurveyFormView(FormMixin, DetailView):
    template_name = 'djf_surveys/form.html'
    success_url = reverse_lazy("djf_surveys:index")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['eligible_users'] = Profile.objects.filter(
            position__slug__in=['boshligi', 'boshligi-orinbosari', 'professori', 'dotsenti', 'katta-oqituvchisi', 'oqituvchisi', 'kabinet-boshligi'],
            can_be_rated=True
        ).order_by('department__name')
        context['questions2'] = Question2.objects.filter(survey=self.object)  # Add Question2 to context
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        if 'create' in request.path:
            questions = Question.objects.filter(survey=self.object)
            for param in request.GET.keys():  # loop over all GET parameters
                for question in questions:
                    if question.key == param:  # find corresponding question
                        field_key = f"field_survey_{question.id}"
                        if field_key in context["form"].field_names:
                            if question.type_field == TYPE_FIELD.rating:
                                if not question.choices:
                                    question.choices = 5
                                context["form"][field_key].field.initial = max(0, min(int(request.GET[param]),
                                                                                      int(question.choices) - 1))
                            elif question.type_field == TYPE_FIELD.multi_select:
                                context["form"][field_key].field.initial = request.GET[param].split(',')
                            else:
                                context["form"][field_key].field.initial = request.GET[param]
                        break

        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()  # Hozirgi so‘rovnoma obyekti
        form = self.get_form()

        if form.is_valid():
            try:
                # Save ma'lumotlar
                form.save()
                messages.success(request, "Javobingiz saqlandi!")
                return self.form_valid(form)
            except Exception as e:
                messages.error(request, f"Saqlashda xatolik yuz berdi: {str(e)}")
                return self.form_invalid(form)
        else:
            messages.error(request, "Formani to‘ldirishda xatolik")
            return self.form_invalid(form)

    def get_form(self, form_class=None):
        form_class = form_class or self.get_form_class()
        return form_class(survey=self.get_object(), user=self.request.user, **self.get_form_kwargs())


class CreateSurveyFormView(ContextTitleMixin, SurveyFormView):
    model = Survey
    form_class = CreateSurveyForm
    title_page = _("So'rovnoma to'ldirish")

    def dispatch(self, request, *args, **kwargs):
        survey = self.get_object()
        if not request.user.is_authenticated and not survey.can_anonymous_user:
            messages.warning(request, gettext("Kechirasiz, so'rovnomani to'ldirish uchun tizimga kirgan bo'lishingiz kerak."))
            return redirect("djf_surveys:index")

        # handle if user have answer survey
        if request.user.is_authenticated and not survey.duplicate_entry and \
                UserAnswer.objects.filter(survey=survey, user=request.user).exists():
            messages.warning(request, gettext("Siz ushbu so'rovnomani topshirdingiz."))
            return redirect("djf_surveys:index")
        return super().dispatch(request, *args, **kwargs)
    
    def get_current_section(self):
        """Get current section from GET parameter or determine first section."""
        survey = self.get_object()
        navigator = SectionNavigator(survey)
        
        # Try to get section from URL parameter
        section_id = self.request.GET.get('section')
        if section_id:
            try:
                return Section.objects.get(id=section_id, survey=survey)
            except Section.DoesNotExist:
                pass
        
        # Check for draft
        draft = DraftService.load_draft(
            survey=survey,
            user=self.request.user if self.request.user.is_authenticated else None,
            session_key=self.request.session.session_key
        )
        if draft and draft.current_section:
            return draft.current_section
        
        # Return first section
        return navigator.get_first_section()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        survey = self.get_object()
        current_section = self.get_current_section()
        navigator = SectionNavigator(survey)
        
        # Get session key for anonymous users
        session_key = None
        if not self.request.user.is_authenticated:
            session_key = self.request.session.session_key
        
        # Add section navigation context
        if current_section:
            context['current_section'] = current_section
            context['is_first_section'] = navigator.is_first_section(current_section)
            
            # Get draft to check for answers
            draft = DraftService.load_draft(
                survey=survey,
                user=self.request.user if self.request.user.is_authenticated else None,
                session_key=session_key
            )
            answers = draft.data if draft else {}
            
            context['is_last_section'] = navigator.is_last_section(current_section, answers)
            current_pos, total = navigator.get_section_progress(current_section)
            context['section_progress'] = {
                'current': current_pos,
                'total': total,
                'percentage': int((current_pos / total) * 100) if total > 0 else 0
            }
        
        # Check for existing draft
        draft = DraftService.load_draft(
            survey=survey,
            user=self.request.user if self.request.user.is_authenticated else None,
            session_key=session_key
        )
        if draft:
            context['has_draft'] = True
            context['draft'] = draft
        
        return context

    def get_form(self, form_class=None):
        form_class = form_class or self.get_form_class()
        current_section = self.get_current_section()
        return form_class(
            survey=self.get_object(),
            user=self.request.user,
            current_section=current_section,
            **self.get_form_kwargs()
        )
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        
        if form.is_valid():
            # Determine action: save_draft, next, previous, or submit
            action = request.POST.get('action', 'next')
            
            if action == 'save_draft':
                # Save as draft
                return self.save_draft(form)
            elif action == 'previous':
                # Navigate to previous section
                return self.navigate_previous()
            elif action in ['next', 'submit']:
                # Save draft and navigate or submit
                return self.handle_next_or_submit(form, action)
        
        return self.form_invalid(form)
    
    def save_draft(self, form):
        """Save current progress as draft."""
        survey = self.get_object()
        current_section = self.get_current_section()
        
        # Ensure session exists for anonymous users
        if not self.request.user.is_authenticated:
            if not self.request.session.session_key:
                self.request.session.create()
        
        # Extract answers from form
        answers = DraftService.extract_answers_from_form(form.cleaned_data)
        
        # Save draft
        DraftService.save_draft(
            survey=survey,
            data=answers,
            user=self.request.user if self.request.user.is_authenticated else None,
            session_key=self.request.session.session_key if not self.request.user.is_authenticated else None,
            current_section=current_section
        )
        
        messages.success(self.request, _("Draft saved successfully"))
        return redirect(self.request.path + f'?section={current_section.id}')
    
    def navigate_previous(self):
        """Navigate to previous section."""
        current_section = self.get_current_section()
        if not current_section:
            return redirect(self.request.path)
        
        navigator = SectionNavigator(self.get_object())
        previous_section = navigator.get_previous_section(current_section)
        
        if previous_section:
            return redirect(self.request.path + f'?section={previous_section.id}')
        
        messages.warning(self.request, _("Already at first section"))
        return redirect(self.request.path + f'?section={current_section.id}')
    
    def handle_next_or_submit(self, form, action):
        """Handle next section navigation or final submission."""
        survey = self.get_object()
        current_section = self.get_current_section()
        
        # Ensure session exists for anonymous users
        if not self.request.user.is_authenticated:
            if not self.request.session.session_key:
                self.request.session.create()
        
        # If survey has sections, use navigation logic
        if current_section:
            navigator = SectionNavigator(survey)
            
            # Extract and save answers to draft first
            answers = DraftService.extract_answers_from_form(form.cleaned_data)
            draft = DraftService.save_draft(
                survey=survey,
                data=answers,
                user=self.request.user if self.request.user.is_authenticated else None,
                session_key=self.request.session.session_key if not self.request.user.is_authenticated else None,
                current_section=current_section
            )
            
            # Determine next section based on branch logic
            next_section = navigator.get_next_section(current_section, draft.data)
            
            if next_section and action == 'next':
                # Navigate to next section
                return redirect(self.request.path + f'?section={next_section.id}')
        
        # Final submission (no sections or last section)
        try:
            form.save()
            # Delete draft after successful submission
            DraftService.delete_draft(
                survey=survey,
                user=self.request.user if self.request.user.is_authenticated else None,
                session_key=self.request.session.session_key if not self.request.user.is_authenticated else None
            )
            messages.success(self.request, _("Survey submitted successfully"))
            return redirect(self.get_success_url())
        except Exception as e:
            messages.error(self.request, f"Error: {str(e)}")
            return self.form_invalid(form)

    def get_title_page(self):
        return self.get_object().name

    def get_sub_title_page(self):
        return self.get_object().description

    def get_success_url(self):
        return reverse("djf_surveys:success", kwargs={"slug": self.get_object().slug})


@method_decorator(login_required, name='dispatch')
class EditSurveyFormView(ContextTitleMixin, SurveyFormView):
    form_class = EditSurveyForm
    title_page = "So‘rovnomani tahrirlash"
    model = UserAnswer

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.get_object().survey
        return context

    def dispatch(self, request, *args, **kwargs):
        # handle if user not same
        user_answer = self.get_object()
        if user_answer.user != request.user or not user_answer.survey.editable:
            messages.warning(request, gettext("Siz bu soʻrovnomani tahrirlay olmaysiz. Sizda ruxsat yo‘q."))
            return redirect("djf_surveys:index")
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        user_answer = self.get_object()
        return form_class(user_answer=user_answer, **self.get_form_kwargs())

    def get_title_page(self):
        return self.get_object().survey.name

    def get_sub_title_page(self):
        return self.get_object().survey.description


@method_decorator(login_required, name='dispatch')
class DeleteSurveyAnswerView(DetailView):
    model = UserAnswer

    def dispatch(self, request, *args, **kwargs):
        # handle if user not same
        user_answer = self.get_object()
        if user_answer.user != request.user or not user_answer.survey.deletable:
            messages.warning(request, gettext("Bu soʻrovnomani oʻchira olmaysiz. Sizda ruxsat yo‘q."))
            return redirect("djf_surveys:index")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        user_answer = self.get_object()
        user_answer.delete()
        messages.success(self.request, gettext("Javob muvaffaqiyatli oʻchirildi."))
        return redirect("djf_surveys:detail", slug=user_answer.survey.slug)


class DetailSurveyView(ContextTitleMixin, DetailView):
    model = Survey
    template_name = "djf_surveys/answer_list.html"
    title_page = _("So'rovnoma tafsilotlari")
    paginate_by = app_settings.SURVEY_PAGINATION_NUMBER['answer_list']

    def dispatch(self, request, *args, **kwargs):
        survey = self.get_object()
        if not self.request.user.is_superuser and survey.private_response:
            messages.warning(request, gettext("Siz bu sahifaga kira olmaysiz. Sizda ruxsat yo‘q."))
            return redirect("djf_surveys:index")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        user_answers = UserAnswer.objects.filter(survey=self.get_object()) \
            .select_related('user').prefetch_related('answer_set__question')
        paginator = NewPaginator(user_answers, self.paginate_by)
        page_number = self.request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        page_range = paginator.get_elided_page_range(number=page_number)
        context = super().get_context_data(**kwargs)
        context['page_obj'] = page_obj
        context['page_range'] = page_range
        return context


@method_decorator(login_required, name='dispatch')
class DetailResultSurveyView(ContextTitleMixin, DetailView):
    title_page = _("So‘rovnoma natijalari")
    template_name = "djf_surveys/detail_result.html"
    model = UserAnswer

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.get_object()
        context['on_detail'] = True
        return context

    def dispatch(self, request, *args, **kwargs):
        # handle if user not same
        user_answer = self.get_object()
        if user_answer.user != request.user:
            messages.warning(request, gettext("Siz bu sahifaga kira olmaysiz. Sizda ruxsat yo‘q."))
            return redirect("djf_surveys:index")
        return super().dispatch(request, *args, **kwargs)

    def get_title_page(self):
        return self.get_object().survey.name

    def get_sub_title_page(self):
        return self.get_object().survey.description


def share_link(request, slug):
    # this func to handle link redirect to create form or edit form
    survey = get_object_or_404(Survey, slug=slug)
    if request.user.is_authenticated:
        user_answer = UserAnswer.objects.filter(survey=survey, user=request.user).last()
        if user_answer:
            return redirect(reverse_lazy("djf_surveys:edit", kwargs={'pk': user_answer.id}))
    return redirect(reverse_lazy("djf_surveys:create", kwargs={'slug': survey.slug}))


class SuccessPageSurveyView(ContextTitleMixin, DetailView):
    model = Survey
    template_name = "djf_surveys/success-page.html"
    title_page = _("Successfully submitted!")


@login_required
def download_survey_file(request, answer_id):
    """
    Protected view to download survey file uploads.
    Only accessible by survey admins or file owner.
    """
    from djf_surveys.models import Answer
    
    try:
        answer = Answer.objects.select_related(
            'user_answer__survey', 'user_answer__user', 'question'
        ).get(id=answer_id)
    except Answer.DoesNotExist:
        raise Http404("File not found")
    
    # Check permissions
    survey = answer.user_answer.survey
    user = request.user
    
    # Allow if: superuser, staff, survey owner, or response owner
    is_admin = user.is_superuser or user.is_staff
    is_owner = answer.user_answer.user == user
    is_public_response = not survey.private_response
    
    if not (is_admin or is_owner or is_public_response):
        return HttpResponseForbidden("You don't have permission to access this file")
    
    # Check if file exists
    if not answer.file_value:
        raise Http404("No file attached to this answer")
    
    file_path = answer.file_value.path
    if not os.path.exists(file_path):
        raise Http404("File not found on server")
    
    # Serve file
    response = FileResponse(open(file_path, 'rb'))
    response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
    return response
