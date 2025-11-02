import codecs
import csv
from io import StringIO
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.text import capfirst
from django.utils.translation import gettext, gettext_lazy as _
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormMixin
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import View
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.db.models import Avg
from accounts.models import Profile
from djf_surveys.app_settings import SURVEYS_ADMIN_BASE_PATH
from djf_surveys.models import Survey, Question, UserAnswer, Answer, Direction, UserRating
from djf_surveys.mixin import ContextTitleMixin
from djf_surveys.views import SurveyListView
from djf_surveys.forms import BaseSurveyForm
from djf_surveys.summary import SummaryResponse
from djf_surveys.admins.v2.forms import SurveyForm
from djf_surveys.utils import get_type_field


@method_decorator(staff_member_required, name='dispatch')
class AdminCrateSurveyView(ContextTitleMixin, CreateView):
    template_name = 'djf_surveys/admins/form.html'
    form_class = SurveyForm
    title_page = _("Yangi so‘rovnoma qo‘shish")

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            survey = form.save()
            self.success_url = reverse("djf_surveys:admin_forms_survey", args=[survey.slug])
            messages.success(self.request, gettext("%(page_action_name)s succeeded.") % dict(page_action_name=capfirst(self.title_page.lower())))
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


@method_decorator(staff_member_required, name='dispatch')
class AdminEditSurveyView(ContextTitleMixin, UpdateView):
    model = Survey
    form_class = SurveyForm
    template_name = 'djf_surveys/admins/form.html'
    title_page = _("Edit survey")

    def get_success_url(self):
        survey = self.get_object()
        return reverse("djf_surveys:admin_forms_survey", args=[survey.slug])


@method_decorator(staff_member_required, name='dispatch')
class AdminSurveyListView(SurveyListView):
    template_name = 'djf_surveys/admins/survey_list.html'


@method_decorator(staff_member_required, name='dispatch')
class AdminSurveyFormView(ContextTitleMixin, FormMixin, DetailView):
    model = Survey
    template_name = 'djf_surveys/admins/form_preview.html'
    form_class = BaseSurveyForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Existing context data...

        # Add eligible_users to context
        context['eligible_users'] = Profile.objects.filter(
            position__slug__in=[
                'boshligi', 'boshligi-orinbosari', 'professori', 'dotsenti',
                'katta-oqituvchisi', 'oqituvchisi', 'kabinet-boshligi'
            ]
        ).distinct()
        
        # Add get_type_field for modal_choice_field_type.html
        context['get_type_field'] = get_type_field()
        
        return context

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(survey=self.object, user=self.request.user, **self.get_form_kwargs())

    def get_title_page(self):
        return self.object.name

    def get_sub_title_page(self):
        return self.object.description

    def dispatch(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
            return self.handle_ajax_request(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)

    def handle_ajax_request(self, request, *args, **kwargs):
        user_id = request.POST.get('user_id')
        can_be_rated = request.POST.get('can_be_rated') == 'true'

        try:
            profile = Profile.objects.get(id=user_id)
            profile.can_be_rated = can_be_rated
            profile.save()
            return JsonResponse({'status': 'success', 'can_be_rated': profile.can_be_rated})
        except Profile.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found.'}, status=404)


@method_decorator(staff_member_required, name='dispatch')
class AdminDeleteSurveyView(DetailView):
    model = Survey

    def get(self, request, *args, **kwargs):
        survey = self.get_object()
        survey.delete()
        messages.success(request, gettext("Survey '%s' deleted successfully.") % survey.name)
        return redirect("djf_surveys:admin_survey")


@method_decorator(staff_member_required, name='dispatch')
class AdminCreateQuestionView(ContextTitleMixin, CreateView):
    """
    Note: This class already has version 2
    """
    model = Question
    template_name = 'djf_surveys/admins/question_form.html'
    success_url = reverse_lazy("djf_surveys:")
    fields = ['label', 'key', 'type_field', 'choices', 'help_text', 'required']
    title_page = _("Savol qo‘shish")
    survey = None

    def dispatch(self, request, *args, **kwargs):
        self.survey = get_object_or_404(Survey, id=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            question = form.save(commit=False)
            question.survey = self.survey
            question.save()
            messages.success(self.request, gettext("%(page_action_name)s succeeded.") % dict(page_action_name=capfirst(self.title_page.lower())))
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse("djf_surveys:admin_forms_survey", args=[self.survey.slug])


@method_decorator(staff_member_required, name='dispatch')
class AdminUpdateQuestionView(ContextTitleMixin, UpdateView):
    """
    Note: This class already has version 2
    """
    model = Question
    template_name = 'djf_surveys/admins/question_form.html'
    success_url = SURVEYS_ADMIN_BASE_PATH
    fields = ['label', 'key', 'type_field', 'choices', 'help_text', 'required']
    title_page = _("Savol qo‘shish")
    survey = None

    def dispatch(self, request, *args, **kwargs):
        question = self.get_object()
        self.survey = question.survey
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("djf_surveys:admin_forms_survey", args=[self.survey.slug])


@method_decorator(staff_member_required, name='dispatch')
class AdminDeleteQuestionView(DetailView):
    model = Question
    survey = None

    def dispatch(self, request, *args, **kwargs):
        question = self.get_object()
        self.survey = question.survey
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        question = self.get_object()
        question.delete()
        messages.success(request, gettext("Question '%s' deleted successfully.") % question.label)
        return redirect("djf_surveys:admin_forms_survey", slug=self.survey.slug)


@method_decorator(staff_member_required, name='dispatch')
class AdminChangeOrderQuestionView(View):
    def post(self, request, *args, **kwargs):
        ordering = request.POST['order_question'].split(",")
        for index, question_id in enumerate(ordering):
            if question_id:
                question = Question.objects.get(id=question_id)
                question.ordering = index
                question.save()

        data = {
            'message': gettext("Update ordering of questions succeeded.")
        }
        return JsonResponse(data, status=200)


@method_decorator(staff_member_required, name='dispatch')
class DownloadResponseSurveyView(DetailView):
    model = Survey

    def get(self, request, *args, **kwargs):
        survey = self.get_object()
        user_answers = UserAnswer.objects.filter(survey=survey)
        csv_buffer = StringIO()
        csv_buffer.write(codecs.BOM_UTF8.decode('utf-8'))

        writer = csv.writer(csv_buffer, delimiter=',')

        # Get all questions for this survey in order
        all_questions = Question.objects.filter(survey=survey).order_by('ordering', 'id')
        
        # Build header
        header = ['user', 'submitted time', 'IP address', 'browser', 'OS', 'device']
        for question in all_questions:
            if question.type_field == 10:  # TYPE_FIELD.file
                # Add two columns for file questions: URL and Local Path
                header.append(f"{question.label} (URL)")
                header.append(f"{question.label} (Local Path)")
            else:
                header.append(question.label)
        writer.writerow(header)

        # Build rows for each user answer
        for user_answer in user_answers:
            rows = []
            rows.append(user_answer.user.username if user_answer.user else 'not registered')
            rows.append(user_answer.updated_at.strftime("%Y-%m-%d %H:%M:%S"))
            rows.append(user_answer.ip_address or 'N/A')
            rows.append(user_answer.browser or 'N/A')
            rows.append(user_answer.os or 'N/A')
            rows.append(user_answer.device or 'N/A')

            # Create a dictionary of answers by question id for quick lookup
            answers_dict = {}
            for answer in user_answer.answer_set.all():
                answers_dict[answer.question.id] = answer

            # For each question, add answer or null
            for question in all_questions:
                if question.id in answers_dict:
                    answer = answers_dict[question.id]
                    # For file uploads, add two separate columns
                    if answer.question.type_field == 10:  # TYPE_FIELD.file
                        rows.append(answer.get_file_url(request))  # URL column
                        rows.append(answer.get_file_local_path())  # Local path column
                    else:
                        rows.append(answer.get_value_for_csv)
                else:
                    # Question not answered - add null
                    if question.type_field == 10:  # TYPE_FIELD.file
                        rows.append('null')  # URL
                        rows.append('null')  # Local path
                    else:
                        rows.append('null')

            writer.writerow(rows)

        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename={survey.slug}.csv'
        response.write(csv_buffer.getvalue())
        return response


@method_decorator(staff_member_required, name='dispatch')
class DownloadFilteredResponseSurveyView(DetailView):
    """Download survey responses with advanced filtering"""
    model = Survey

    def get(self, request, *args, **kwargs):
        survey = self.get_object()
        
        # Get filter parameters
        from_date = request.GET.get('from_date', None)
        to_date = request.GET.get('to_date', None)
        selected_year = request.GET.get('year', None)
        selected_month = request.GET.get('month', None)
        selected_direction_id = request.GET.get('direction', None)
        selected_question_ids = request.GET.getlist('questions')
        
        # Build queryset with filters
        user_answers = UserAnswer.objects.filter(survey=survey)
        
        # Apply date range filters
        if from_date:
            from datetime import datetime
            try:
                from_datetime = datetime.strptime(from_date, '%Y-%m-%d')
                user_answers = user_answers.filter(created_at__gte=from_datetime)
            except ValueError:
                pass
        
        if to_date:
            from datetime import datetime, timedelta
            try:
                to_datetime = datetime.strptime(to_date, '%Y-%m-%d')
                to_datetime = to_datetime + timedelta(days=1)
                user_answers = user_answers.filter(created_at__lt=to_datetime)
            except ValueError:
                pass
        
        # If no date range, use year/month filters
        if not from_date and not to_date:
            if selected_year and selected_year.isdigit():
                user_answers = user_answers.filter(created_at__year=int(selected_year))
            if selected_month and selected_month.isdigit():
                user_answers = user_answers.filter(created_at__month=int(selected_month))
        
        # Apply direction filter
        if selected_direction_id:
            try:
                direction = Direction.objects.get(id=selected_direction_id)
                user_answers = user_answers.filter(direction=direction)
            except Direction.DoesNotExist:
                pass
        
        # Get questions to include
        if selected_question_ids:
            question_ids = [int(q_id) for q_id in selected_question_ids if q_id.isdigit()]
            all_questions = Question.objects.filter(survey=survey, id__in=question_ids).order_by('ordering', 'id')
        else:
            all_questions = Question.objects.filter(survey=survey).order_by('ordering', 'id')
        
        # Build CSV
        csv_buffer = StringIO()
        csv_buffer.write(codecs.BOM_UTF8.decode('utf-8'))
        writer = csv.writer(csv_buffer, delimiter=',')
        
        # Build header with filter info
        filter_info = []
        if from_date:
            filter_info.append(f"From: {from_date}")
        if to_date:
            filter_info.append(f"To: {to_date}")
        if selected_direction_id:
            try:
                direction = Direction.objects.get(id=selected_direction_id)
                filter_info.append(f"Course: {direction.name}")
            except:
                pass
        
        if filter_info:
            writer.writerow([f"Filters: {', '.join(filter_info)}"])
            writer.writerow([])  # Empty row
        
        # Column headers
        header = ['User', 'Direction', 'Submitted Time', 'IP Address', 'Browser', 'OS', 'Device']
        for question in all_questions:
            if question.type_field == 10:  # TYPE_FIELD.file
                # Add two columns for file questions: URL and Local Path
                header.append(f"{question.label} (URL)")
                header.append(f"{question.label} (Local Path)")
            else:
                header.append(question.label)
        writer.writerow(header)
        
        # Data rows
        for user_answer in user_answers:
            rows = []
            rows.append(user_answer.user.username if user_answer.user else 'Guest')
            rows.append(user_answer.direction.name if user_answer.direction else 'N/A')
            rows.append(user_answer.updated_at.strftime("%Y-%m-%d %H:%M:%S"))
            rows.append(user_answer.ip_address or 'N/A')
            rows.append(user_answer.browser or 'N/A')
            rows.append(user_answer.os or 'N/A')
            rows.append(user_answer.device or 'N/A')
            
            # Create answer lookup dictionary
            answers_dict = {}
            for answer in user_answer.answer_set.all():
                answers_dict[answer.question.id] = answer
            
            # Add answer values for each question
            for question in all_questions:
                if question.id in answers_dict:
                    answer = answers_dict[question.id]
                    if answer.question.type_field == 10:  # TYPE_FIELD.file
                        rows.append(answer.get_file_url(request))  # URL column
                        rows.append(answer.get_file_local_path())  # Local path column
                    else:
                        rows.append(answer.get_value_for_csv)
                else:
                    if question.type_field == 10:  # TYPE_FIELD.file
                        rows.append('N/A')  # URL
                        rows.append('N/A')  # Local path
                    else:
                        rows.append('N/A')
            
            writer.writerow(rows)
        
        # Generate filename with filter info
        filename_parts = [survey.slug]
        if from_date:
            filename_parts.append(f"from-{from_date}")
        if to_date:
            filename_parts.append(f"to-{to_date}")
        filename = "_".join(filename_parts) + ".csv"
        
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        response.write(csv_buffer.getvalue())
        return response


@method_decorator(staff_member_required, name='dispatch')
class SummaryResponseSurveyView(ContextTitleMixin, DetailView):
    model = Survey
    template_name = "djf_surveys/admins/summary.html"
    title_page = _("Summary")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        survey = self.get_object()

        current_year = now().year
        selected_year = self.request.GET.get('year', None)
        try:
            selected_year = int(selected_year) if selected_year else current_year
        except ValueError:
            selected_year = None

        selected_month = self.request.GET.get('month', None)
        if selected_month and selected_month.isdigit():
            selected_month = int(selected_month)
        else:
            selected_month = None

        selected_direction_id = self.request.GET.get('direction')

        selected_direction = None
        if selected_direction_id:
            try:
                selected_direction = Direction.objects.get(id=selected_direction_id)
            except Direction.DoesNotExist:
                selected_direction = None
        else:
            selected_direction = None

        # Get date range filters
        from_date = self.request.GET.get('from_date', None)
        to_date = self.request.GET.get('to_date', None)
        
        # Get selected questions filter
        selected_question_ids = self.request.GET.getlist('questions')
        selected_questions = [int(q_id) for q_id in selected_question_ids if q_id.isdigit()]

        directions = Direction.objects.all()

        answer_queryset = Answer.objects.all()

        if selected_year:
            answer_queryset = answer_queryset.filter(created_at__year=selected_year)

        if selected_month:
            answer_queryset = answer_queryset.filter(created_at__month=selected_month)

        if selected_direction:
            answer_queryset = answer_queryset.filter(user_answer__direction=selected_direction)

        rated_users = (
            UserRating.objects
                .filter(user_answer__survey=survey)  # Ratings for this survey
                .values(
                "rated_user__first_name",
                "rated_user__last_name",
            )
                .annotate(avg_rating=Avg("answer2__value"))  # Average rating
                .order_by("-avg_rating")  # Highest to lowest
        )

        summary = SummaryResponse(
            survey=survey,
            selected_year=selected_year if selected_year else None,
            selected_month=selected_month if selected_month else None,
            selected_direction=selected_direction if selected_direction else None,
            from_date=from_date,
            to_date=to_date,
            selected_questions=selected_questions
        )

        # Generate year and month ranges for the form
        years = range(2024, current_year + 1)
        months = [
            {'value': 1, 'name': 'January'},
            {'value': 2, 'name': 'February'},
            {'value': 3, 'name': 'March'},
            {'value': 4, 'name': 'April'},
            {'value': 5, 'name': 'May'},
            {'value': 6, 'name': 'June'},
            {'value': 7, 'name': 'July'},
            {'value': 8, 'name': 'August'},
            {'value': 9, 'name': 'September'},
            {'value': 10, 'name': 'October'},
            {'value': 11, 'name': 'November'},
            {'value': 12, 'name': 'December'}
        ]

        # Get all questions for the survey (for filter dropdown)
        all_questions = Question.objects.filter(survey=survey).order_by('ordering', 'id')
        
        context.update({
            'summary': summary,
            'years': years,
            'selected_year': selected_year,
            'months': months,
            'selected_month': selected_month,
            'directions': directions,
            'selected_direction': selected_direction,
            'rated_users': rated_users,
            'from_date': from_date,
            'to_date': to_date,
            'all_questions': all_questions,
            'selected_questions': selected_questions,
        })
        return context


class DirectionsListView(View):
    template_name = "djf_surveys/admins/directions.html"

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        directions_qs = Direction.objects.all().order_by('name')

        context = {
            'directions_qs': directions_qs,
        }
        return render(request, self.template_name, context)


class DirectionUpdateView(UpdateView):
    model = Direction
    fields = ["name"]
    template_name = "djf_surveys/admins/direction_update.html"
    success_url = reverse_lazy("djf_surveys:directions")


class DirectionDeleteView(LoginRequiredMixin, DeleteView):
    model = Direction
    template_name = "djf_surveys/admins/direction_delete.html"
    success_url = reverse_lazy("djf_surveys:directions")


class DirectionAddView(LoginRequiredMixin, CreateView):
    model = Direction
    fields = ["name"]
    template_name = "djf_surveys/admins/add_direction.html"
    success_url = reverse_lazy("djf_surveys:directions")