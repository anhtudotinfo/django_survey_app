from django.urls import path
from djf_surveys.admins import views as admin_views
from djf_surveys.admins.v2 import views as admin_views_v2
from djf_surveys.admins.views import DirectionsListView, DirectionUpdateView, DirectionDeleteView, DirectionAddView
from djf_surveys.admins import api_views

urlpatterns = [
    path('', admin_views.AdminSurveyListView.as_view(), name='admin_survey'),
    path('create/survey/', admin_views.AdminCrateSurveyView.as_view(), name='admin_create_survey'),
    path('edit/survey/<str:slug>/', admin_views.AdminEditSurveyView.as_view(), name='admin_edit_survey'),
    path('delete/survey/<str:slug>/', admin_views.AdminDeleteSurveyView.as_view(), name='admin_delete_survey'),
    path('forms/<str:slug>/', admin_views.AdminSurveyFormView.as_view(), name='admin_forms_survey'),
    path('question/add/<int:pk>/<int:type_field>', admin_views_v2.AdminCreateQuestionView.as_view(),
         name='admin_create_question'),
    path('question/edit/<int:pk>/', admin_views_v2.AdminUpdateQuestionView.as_view(), name='admin_edit_question'),
    path('question/delete/<int:pk>/', admin_views.AdminDeleteQuestionView.as_view(), name='admin_delete_question'),
    path('question/ordering/', admin_views.AdminChangeOrderQuestionView.as_view(), name='admin_change_order_question'),
    path('download/survey/<str:slug>/', admin_views.DownloadResponseSurveyView.as_view(), name='admin_download_survey'),
    path('download/filtered/<str:slug>/', admin_views.DownloadFilteredResponseSurveyView.as_view(), name='admin_download_filtered_survey'),
    path('summary/survey/<str:slug>/', admin_views.SummaryResponseSurveyView.as_view(), name='admin_summary_survey'),
    path('directions/', DirectionsListView.as_view(), name='directions'),
    path('directions/add/', DirectionAddView.as_view(), name='add-direction'),
    path('directions/edit/<int:pk>/', DirectionUpdateView.as_view(), name='edit_direction'),
    path('directions/delete/<int:pk>/', DirectionDeleteView.as_view(), name='delete_direction'),
    
    # API endpoints for enhanced survey builder
    path('api/survey/<slug:slug>/sections/', api_views.SurveySectionsAPIView.as_view(), name='api_survey_sections'),
    path('api/section/create/', api_views.SectionCreateAPIView.as_view(), name='api_section_create'),
    path('api/section/<int:pk>/update/', api_views.SectionUpdateAPIView.as_view(), name='api_section_update'),
    path('api/section/<int:pk>/delete/', api_views.SectionDeleteAPIView.as_view(), name='api_section_delete'),
    path('api/sections/reorder/', api_views.SectionsReorderAPIView.as_view(), name='api_sections_reorder'),
    path('api/question/<int:pk>/move/', api_views.QuestionMoveAPIView.as_view(), name='api_question_move'),
    path('api/question/<int:pk>/delete/', api_views.QuestionDeleteAPIView.as_view(), name='api_question_delete'),
]
