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
from djf_surveys.models import (Survey, UserAnswer, UserAnswer2, Question,
                                Question2, TYPE_FIELD, Answer2, UserRating,
                                Section)
from djf_surveys.forms import CreateSurveyForm, EditSurveyForm
from djf_surveys.mixin import ContextTitleMixin
from djf_surveys import app_settings
from djf_surveys.utils import NewPaginator
from djf_surveys.navigation import SectionNavigator
from djf_surveys.draft_service import DraftService


class SurveyListView(ContextTitleMixin, UserPassesTestMixin, ListView):
    model = Survey
    title_page = "List of questionnaires"
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
            object_list = self.model.objects.filter(name__icontains=query,
                                                    **filter)
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
        page_range = context['page_obj'].paginator.get_elided_page_range(
            number=page_number)
        context['page_range'] = page_range

        # Generate QR codes with full domain for all surveys
        surveys_with_qr = []
        for survey in context['object_list']:
            survey.qr_code_with_domain = survey.generate_qr_code(self.request)
            surveys_with_qr.append(survey)
        context['object_list'] = surveys_with_qr

        return context


class SurveyFormView(FormMixin, DetailView):
    template_name = 'djf_surveys/form.html'
    success_url = reverse_lazy("djf_surveys:index")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['eligible_users'] = Profile.objects.filter(
            position__slug__in=[
                'boshligi', 'boshligi-orinbosari', 'professori', 'dotsenti',
                'katta-oqituvchisi', 'oqituvchisi', 'kabinet-boshligi'
            ],
            can_be_rated=True).order_by('department__name')
        context['questions2'] = Question2.objects.filter(
            survey=self.object)  # Add Question2 to context
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
                                context["form"][field_key].field.initial = max(
                                    0,
                                    min(int(request.GET[param]),
                                        int(question.choices) - 1))
                            elif question.type_field == TYPE_FIELD.multi_select:
                                context["form"][
                                    field_key].field.initial = request.GET[
                                        param].split(',')
                            else:
                                context["form"][
                                    field_key].field.initial = request.GET[
                                        param]
                        break

        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()  # Hozirgi so‘rovnoma obyekti
        form = self.get_form()

        if form.is_valid():
            try:
                # Save ma'lumotlar
                form.save()
                messages.success(request, "Your response has been saved!")
                return self.form_valid(form)
            except Exception as e:
                messages.error(request,
                               f"An error occurred while saving: {str(e)}")
                return self.form_invalid(form)
        else:
            messages.error(request, "Error filling out the form")
            return self.form_invalid(form)

    def get_form(self, form_class=None):
        form_class = form_class or self.get_form_class()
        return form_class(survey=self.get_object(),
                          user=self.request.user,
                          **self.get_form_kwargs())


class CreateSurveyFormView(ContextTitleMixin, SurveyFormView):
    model = Survey
    form_class = CreateSurveyForm
    title_page = _("Fill Survey")

    def dispatch(self, request, *args, **kwargs):
        survey = self.get_object()
        if not request.user.is_authenticated and not survey.can_anonymous_user:
            messages.warning(
                request,
                gettext(
                    "Sorry, you need to be logged in to fill out the survey."))
            return redirect("djf_surveys:index")

        # handle if user have answer survey
        if request.user.is_authenticated and not survey.duplicate_entry and \
                UserAnswer.objects.filter(survey=survey, user=request.user).exists():
            messages.warning(
                request, gettext("You have already submitted this survey."))
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
            user=self.request.user
            if self.request.user.is_authenticated else None,
            session_key=self.request.session.session_key)
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
            context['is_first_section'] = navigator.is_first_section(
                current_section)

            # Get draft to check for answers
            draft = DraftService.load_draft(
                survey=survey,
                user=self.request.user
                if self.request.user.is_authenticated else None,
                session_key=session_key)
            answers = draft.data if draft else {}

            context['is_last_section'] = navigator.is_last_section(
                current_section, answers)
            current_pos, total = navigator.get_section_progress(
                current_section)
            context['section_progress'] = {
                'current': current_pos,
                'total': total,
                'percentage': int(
                    (current_pos / total) * 100) if total > 0 else 0
            }

        # Check for existing draft
        draft = DraftService.load_draft(
            survey=survey,
            user=self.request.user
            if self.request.user.is_authenticated else None,
            session_key=session_key)
        if draft:
            context['has_draft'] = True
            context['draft'] = draft

        return context

    def get_form(self, form_class=None):
        form_class = form_class or self.get_form_class()
        current_section = self.get_current_section()
        survey = self.get_object()

        # Get or create UserAnswer for this session
        user_answer = self._get_or_create_user_answer()

        return form_class(survey=survey,
                          user=self.request.user,
                          current_section=current_section,
                          user_answer=user_answer,
                          **self.get_form_kwargs())

    def _get_or_create_user_answer(self):
        """Get or create UserAnswer for current survey session."""
        from .utils import capture_device_info

        survey = self.get_object()
        device_info = capture_device_info(self.request)

        if self.request.user.is_authenticated:
            # Check session first
            user_answer_id = self.request.session.get(
                f'survey_{survey.id}_user_answer_id')
            if user_answer_id:
                try:
                    return UserAnswer.objects.get(id=user_answer_id,
                                                  user=self.request.user)
                except UserAnswer.DoesNotExist:
                    pass

            # Create new UserAnswer
            if survey.duplicate_entry:
                user_answer = UserAnswer.objects.create(survey=survey,
                                                        user=self.request.user,
                                                        direction=None,
                                                        **device_info)
            else:
                defaults = {'direction': None}
                defaults.update(device_info)
                user_answer, created = UserAnswer.objects.get_or_create(
                    survey=survey, user=self.request.user, defaults=defaults)

            self.request.session[
                f'survey_{survey.id}_user_answer_id'] = user_answer.id
            return user_answer
        else:
            # For anonymous users
            session_key = self.request.session.session_key
            if not session_key:
                self.request.session.create()
                session_key = self.request.session.session_key

            user_answer_id = self.request.session.get(
                f'survey_{survey.id}_user_answer_id')
            if user_answer_id:
                try:
                    return UserAnswer.objects.get(id=user_answer_id)
                except UserAnswer.DoesNotExist:
                    pass

            user_answer = UserAnswer.objects.create(survey=survey,
                                                    user=None,
                                                    direction=None,
                                                    **device_info)
            self.request.session[
                f'survey_{survey.id}_user_answer_id'] = user_answer.id
            return user_answer

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
            user=self.request.user
            if self.request.user.is_authenticated else None,
            session_key=self.request.session.session_key
            if not self.request.user.is_authenticated else None,
            current_section=current_section)

        messages.success(self.request, _("Draft saved successfully"))
        return redirect(self.request.path + f'?section={current_section.id}')

    def navigate_previous(self):
        """Navigate to previous section using navigation history."""
        survey = self.get_object()
        current_section = self.get_current_section()

        if not current_section:
            return redirect(self.request.path)

        # Try to get from URL parameter first (simple approach)
        prev_section_id = self.request.GET.get('prev')
        if prev_section_id:
            try:
                previous_section = Section.objects.get(id=prev_section_id,
                                                       survey=survey)
                return redirect(self.request.path +
                                f'?section={previous_section.id}')
            except (Section.DoesNotExist, ValueError):
                pass

        # Fallback: Get from session history
        history_key = f'survey_{survey.id}_history'
        history = self.request.session.get(history_key, [])

        if history:
            # Pop last section from history
            previous_section_id = history.pop()
            self.request.session[history_key] = history
            self.request.session.modified = True

            try:
                previous_section = Section.objects.get(id=previous_section_id,
                                                       survey=survey)
                return redirect(self.request.path +
                                f'?section={previous_section.id}')
            except Section.DoesNotExist:
                pass

        # Last fallback: Sequential navigation
        navigator = SectionNavigator(survey)
        previous_section = navigator.get_previous_section(current_section)

        if previous_section:
            return redirect(self.request.path +
                            f'?section={previous_section.id}')

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

            # Save answers for current section's questions to database
            # (Not just draft - we need actual Answer records for statistics)
            self._save_current_section_answers(form, current_section)

            # Also save to draft for progress tracking
            answers = DraftService.extract_answers_from_form(form.cleaned_data)
            draft = DraftService.save_draft(
                survey=survey,
                data=answers,
                user=self.request.user
                if self.request.user.is_authenticated else None,
                session_key=self.request.session.session_key
                if not self.request.user.is_authenticated else None,
                current_section=current_section)

            # Determine next section based on branch logic
            next_section = navigator.get_next_section(current_section,
                                                      draft.data)

            if next_section and action == 'next':
                # Save navigation history in session
                history_key = f'survey_{survey.id}_history'
                history = self.request.session.get(history_key, [])
                history.append(current_section.id)
                self.request.session[history_key] = history
                self.request.session.modified = True

                # Navigate to next section with prev parameter
                return redirect(
                    self.request.path +
                    f'?section={next_section.id}&prev={current_section.id}')

        # Final submission (no sections or last section)
        try:
            # For multi-section surveys, answers are already saved via _save_current_section_answers
            # Only call form.save() for non-section surveys
            if not current_section:
                form.save()

            # Delete draft after successful submission
            DraftService.delete_draft(
                survey=survey,
                user=self.request.user
                if self.request.user.is_authenticated else None,
                session_key=self.request.session.session_key
                if not self.request.user.is_authenticated else None)

            # Clear session user_answer_id
            session_key = f'survey_{survey.id}_user_answer_id'
            if session_key in self.request.session:
                del self.request.session[session_key]

            messages.success(self.request, _("Survey submitted successfully"))
            return redirect(self.get_success_url())
        except Exception as e:
            messages.error(self.request, f"Error: {str(e)}")
            return self.form_invalid(form)

    def _save_current_section_answers(self, form, current_section):
        """
        Save answers for current section's questions immediately.
        This ensures answers are saved even when navigating between sections with branching.
        """
        from .models import Answer, UserAnswer
        from .utils import capture_device_info

        survey = self.get_object()

        # Capture device info for security
        device_info = capture_device_info(self.request)

        # Get or create UserAnswer for this survey session
        if self.request.user.is_authenticated:
            # Check if we have a user_answer_id in session (for duplicate_entry surveys)
            user_answer_id = self.request.session.get(
                f'survey_{survey.id}_user_answer_id')
            if user_answer_id:
                try:
                    user_answer = UserAnswer.objects.get(
                        id=user_answer_id, user=self.request.user)
                    created = False
                except UserAnswer.DoesNotExist:
                    # Session had invalid ID, create new one
                    user_answer = UserAnswer.objects.create(
                        survey=survey,
                        user=self.request.user,
                        direction=None,
                        **device_info)
                    created = True
                    self.request.session[
                        f'survey_{survey.id}_user_answer_id'] = user_answer.id
            else:
                # No session ID, try to get existing or create new
                if survey.duplicate_entry:
                    # For duplicate entry surveys, always create new
                    user_answer = UserAnswer.objects.create(
                        survey=survey,
                        user=self.request.user,
                        direction=None,
                        **device_info)
                    created = True
                    self.request.session[
                        f'survey_{survey.id}_user_answer_id'] = user_answer.id
                else:
                    # For non-duplicate surveys, get_or_create is safe
                    defaults = {'direction': None}
                    defaults.update(device_info)
                    user_answer, created = UserAnswer.objects.get_or_create(
                        survey=survey,
                        user=self.request.user,
                        defaults=defaults)
                    self.request.session[
                        f'survey_{survey.id}_user_answer_id'] = user_answer.id
        else:
            # For anonymous users, use session key
            session_key = self.request.session.session_key
            if not session_key:
                self.request.session.create()
                session_key = self.request.session.session_key

            # Store in session to track across sections
            user_answer_id = self.request.session.get(
                f'survey_{survey.id}_user_answer_id')
            if user_answer_id:
                try:
                    user_answer = UserAnswer.objects.get(id=user_answer_id)
                except UserAnswer.DoesNotExist:
                    user_answer = UserAnswer.objects.create(survey=survey,
                                                            user=None,
                                                            direction=None,
                                                            **device_info)
                    self.request.session[
                        f'survey_{survey.id}_user_answer_id'] = user_answer.id
            else:
                user_answer = UserAnswer.objects.create(survey=survey,
                                                        user=None,
                                                        direction=None,
                                                        **device_info)
                self.request.session[
                    f'survey_{survey.id}_user_answer_id'] = user_answer.id

        # Save answers for questions in current section
        questions = form.questions.filter(section=current_section)

        for question in questions:
            field_name = f'field_survey_{question.id}'

            if field_name in form.cleaned_data:
                value = form.cleaned_data[field_name]

                # Prepare defaults based on question type
                if question.type_field == TYPE_FIELD.file:
                    # For file uploads, save to file_value field
                    defaults = {
                        'value': '',  # Empty string for file fields
                        'file_value': value
                    }
                elif isinstance(value, list):
                    # For multi-select, join values
                    defaults = {'value': ",".join(value)}
                else:
                    # For other types, save directly
                    defaults = {'value': value}

                # Update or create answer
                Answer.objects.update_or_create(question=question,
                                                user_answer=user_answer,
                                                defaults=defaults)

        return user_answer

    def get_title_page(self):
        return self.get_object().name

    def get_sub_title_page(self):
        return self.get_object().description

    def get_success_url(self):
        return reverse("djf_surveys:success",
                       kwargs={"slug": self.get_object().slug})


@method_decorator(login_required, name='dispatch')
class EditSurveyFormView(ContextTitleMixin, SurveyFormView):
    form_class = EditSurveyForm
    title_page = "Edit Survey"
    model = UserAnswer

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_answer = self.get_object()
        context['object'] = user_answer.survey
        # Fix: Override questions2 to use correct survey
        context['questions2'] = Question2.objects.filter(
            survey=user_answer.survey)
        return context

    def dispatch(self, request, *args, **kwargs):
        # handle if user not same
        user_answer = self.get_object()
        if user_answer.user != request.user or not user_answer.survey.editable:
            messages.warning(
                request,
                gettext(
                    "You cannot edit this survey. You don't have permission."))
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
            messages.warning(
                request,
                gettext(
                    "You cannot delete this survey. You don't have permission."
                ))
            return redirect("djf_surveys:index")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        user_answer = self.get_object()
        user_answer.delete()
        messages.success(self.request,
                         gettext("Response successfully deleted."))
        return redirect("djf_surveys:detail", slug=user_answer.survey.slug)


@method_decorator(login_required, name='dispatch')
class DetailSurveyView(ContextTitleMixin, DetailView):
    model = Survey
    template_name = "djf_surveys/answer_list.html"
    title_page = _("Survey Details")
    paginate_by = app_settings.SURVEY_PAGINATION_NUMBER['answer_list']

    def dispatch(self, request, *args, **kwargs):
        survey = self.get_object()
        if not self.request.user.is_superuser and survey.private_response:
            messages.warning(
                request,
                gettext(
                    "You cannot access this page. You don't have permission."))
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
        user_answer = self.get_object()
        context['object'] = user_answer
        context['on_detail'] = True

        # Get all questions for the survey
        all_questions = Question.objects.filter(
            survey=user_answer.survey).order_by('id')

        # Create a list of (question, answer) tuples
        # If answer doesn't exist, use None
        answers_dict = {
            answer.question.id: answer
            for answer in user_answer.answer_set.all()
        }
        question_answer_pairs = []
        for question in all_questions:
            answer = answers_dict.get(question.id, None)
            question_answer_pairs.append({
                'question': question,
                'answer': answer
            })

        context['question_answer_pairs'] = question_answer_pairs
        return context

    def dispatch(self, request, *args, **kwargs):
        # handle if user not same
        user_answer = self.get_object()
        if user_answer.user != request.user:
            messages.warning(
                request,
                gettext(
                    "You cannot access this page. You don't have permission."))
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
        user_answer = UserAnswer.objects.filter(survey=survey,
                                                user=request.user).last()
        if user_answer:
            return redirect(
                reverse_lazy("djf_surveys:edit", kwargs={'pk':
                                                         user_answer.id}))
    return redirect(
        reverse_lazy("djf_surveys:create", kwargs={'slug': survey.slug}))


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
        answer = Answer.objects.select_related('user_answer__survey',
                                               'user_answer__user',
                                               'question').get(id=answer_id)
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
        return HttpResponseForbidden(
            "You don't have permission to access this file")

    # Check if file exists
    if not answer.file_value:
        raise Http404("No file attached to this answer")

    file_path = answer.file_value.path
    if not os.path.exists(file_path):
        raise Http404("File not found on server")

    # Serve file
    response = FileResponse(open(file_path, 'rb'))
    response[
        'Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
    return response


def survey_qr_code(request, slug):
    """Display QR code for survey."""
    from django.shortcuts import render
    survey = get_object_or_404(Survey, slug=slug)
    qr_code_data = survey.generate_qr_code(request)

    context = {
        'survey': survey,
        'qr_code': qr_code_data,
        'survey_url': request.build_absolute_uri(survey.get_absolute_url()),
    }
    return render(request, 'djf_surveys/qr_code.html', context)


def survey_qr_download(request, slug):
    """Download QR code as PNG file."""
    from django.http import HttpResponse
    import qrcode
    import io

    survey = get_object_or_404(Survey, slug=slug)
    survey_url = request.build_absolute_uri(survey.get_absolute_url())

    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(survey_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Save to buffer
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    # Return as downloadable file
    response = HttpResponse(buffer.getvalue(), content_type='image/png')
    response[
        'Content-Disposition'] = f'attachment; filename="survey_{survey.slug}_qr.png"'
    return response


@login_required
def download_survey_files(request, slug):
    """
    Download all uploaded files for a survey as a ZIP archive.
    
    Only accessible by staff/admin users.
    """
    from django.http import HttpResponse, HttpResponseForbidden
    from django.conf import settings
    import zipfile
    import io
    import os
    from datetime import datetime

    # Check permissions
    if not request.user.is_staff:
        return HttpResponseForbidden(
            "You don't have permission to download survey files")

    survey = get_object_or_404(Survey, slug=slug)

    # Get all uploaded files
    uploaded_files = survey.get_all_uploaded_files()

    if not uploaded_files.exists():
        messages.warning(request,
                         "No files have been uploaded for this survey yet.")
        return redirect('djf_surveys:admin_summary_survey', slug=slug)

    # Create ZIP file in memory
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add a README file with survey info
        readme_content = f"""Survey Files Download
=====================

Survey Name: {survey.name}
Survey ID: {survey.id}
Organization Type: {survey.get_file_organization_display()}
Download Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total Files: {uploaded_files.count()}

File Organization:
"""
        if survey.file_organization == 'response':
            readme_content += """- Files are organized by response/submission
- Each folder represents one user's submission
- Filename format: Q{question_id}_{timestamp}_{original_name}
"""
        else:
            readme_content += """- Files are organized by question
- Each folder contains files for one specific question
- Filename format: R{response_id}_{timestamp}_{original_name}
"""

        readme_content += f"\nFile Mapping:\n"
        readme_content += "-" * 80 + "\n"

        # Add files to ZIP
        added_files = 0
        for answer in uploaded_files:
            if answer.file_value:
                try:
                    file_path = os.path.join(settings.MEDIA_ROOT,
                                             answer.file_value.name)

                    if os.path.exists(file_path):
                        # Add file to ZIP with its relative path
                        arcname = answer.file_value.name
                        zip_file.write(file_path, arcname)
                        added_files += 1

                        # Add to README
                        user = answer.user_answer.user
                        username = user.username if user else "Anonymous"
                        readme_content += f"\nFile: {arcname}\n"
                        readme_content += f"  Question: {answer.question.label[:50]}\n"
                        readme_content += f"  Response ID: {answer.user_answer.id}\n"
                        readme_content += f"  User: {username}\n"
                        readme_content += f"  Uploaded: {answer.created_at.strftime('%Y-%m-%d %H:%M')}\n"

                except Exception as e:
                    # Log error but continue
                    readme_content += f"\nError accessing file: {answer.file_value.name}\n"
                    readme_content += f"  Error: {str(e)}\n"

        # Add statistics
        stats = survey.get_file_statistics()
        readme_content += f"\n{'='*80}\n"
        readme_content += f"Statistics:\n"
        readme_content += f"  Total files added to ZIP: {added_files}\n"
        readme_content += f"  Total size: {stats['total_size_mb']} MB\n"

        # Add README to ZIP
        zip_file.writestr('README.txt', readme_content)

        # Add file list as CSV
        csv_content = "File Path,Question,Response ID,User,Upload Date\n"
        for answer in uploaded_files:
            if answer.file_value:
                user = answer.user_answer.user
                username = user.username if user else "Anonymous"
                csv_content += f'"{answer.file_value.name}","{answer.question.label}",{answer.user_answer.id},"{username}","{answer.created_at.strftime("%Y-%m-%d %H:%M")}"\n'

        zip_file.writestr('file_list.csv', csv_content)

    # Prepare response
    zip_buffer.seek(0)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'survey_{survey.slug}_files_{timestamp}.zip'

    response = HttpResponse(zip_buffer.getvalue(),
                            content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    messages.success(
        request,
        f"Successfully downloaded {added_files} files from survey '{survey.name}'"
    )

    return response


# Static Pages Views
def about_page(request):
    """About page with content from SiteConfig."""
    from djf_surveys.models import SiteConfig
    config = SiteConfig.get_active()

    return render(
        request, 'djf_surveys/static_pages/about.html', {
            'title': 'About Us',
            'content': config.about_page_content if config else '',
        })


def contact_page(request):
    """Contact page with content from SiteConfig."""
    from djf_surveys.models import SiteConfig
    config = SiteConfig.get_active()

    return render(
        request, 'djf_surveys/static_pages/contact.html', {
            'title': 'Contact Us',
            'content': config.contact_page_content if config else '',
        })


def terms_page(request):
    """Terms & Conditions page with content from SiteConfig."""
    from djf_surveys.models import SiteConfig
    config = SiteConfig.get_active()

    return render(
        request, 'djf_surveys/static_pages/terms.html', {
            'title': 'Terms & Conditions',
            'content': config.terms_page_content if config else '',
        })


def privacy_page(request):
    """Privacy Policy page with content from SiteConfig."""
    from djf_surveys.models import SiteConfig
    config = SiteConfig.get_active()

    return render(
        request, 'djf_surveys/static_pages/privacy.html', {
            'title': 'Privacy Policy',
            'content': config.privacy_page_content if config else '',
        })
