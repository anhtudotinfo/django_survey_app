"""
API views for survey builder enhancements.

These views provide REST-style endpoints for dynamic section and question management
in the admin interface.

Security:
    - All views require staff member authentication
    - CSRF protection enabled on all mutating operations
    - Input validation on all parameters

Endpoints:
    - GET  /api/survey/<slug>/sections/ - Fetch survey structure
    - POST /api/section/create/ - Create new section
    - PATCH /api/section/<pk>/update/ - Update section details
    - DELETE /api/section/<pk>/delete/ - Delete section
    - POST /api/sections/reorder/ - Bulk reorder sections
    - POST /api/question/<pk>/move/ - Move question between sections
    - DELETE /api/question/<pk>/delete/ - Delete question
"""

import json
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import get_object_or_404
from django.db import transaction
from djf_surveys.models import Survey, Section, Question


@method_decorator(staff_member_required, name='dispatch')
@method_decorator(csrf_protect, name='dispatch')
class SurveySectionsAPIView(View):
    """
    Get all sections and questions for a survey.
    
    Returns complete survey structure including sections, questions,
    and unassigned questions for the section manager UI.
    
    Args:
        slug: Survey slug identifier
        
    Returns:
        JSON response with survey data, sections array, and unassigned questions
        
    Example response:
        {
            "survey": {"id": 1, "name": "Student Feedback", "slug": "student-feedback"},
            "sections": [
                {
                    "id": 1,
                    "name": "General Info",
                    "description": "Basic information",
                    "ordering": 0,
                    "questions": [{"id": 1, "label": "Name", ...}]
                }
            ],
            "unassigned_questions": []
        }
    """
    
    def get(self, request, slug):
        survey = get_object_or_404(Survey, slug=slug)
        sections = Section.objects.filter(survey=survey).prefetch_related('questions').order_by('ordering')
        unassigned = Question.objects.filter(survey=survey, section__isnull=True).order_by('ordering')
        
        return JsonResponse({
            'survey': {
                'id': survey.id,
                'name': survey.name,
                'slug': survey.slug
            },
            'sections': [
                {
                    'id': s.id,
                    'name': s.name,
                    'description': s.description,
                    'ordering': s.ordering,
                    'questions': [
                        {
                            'id': q.id,
                            'label': q.label,
                            'type_field': q.type_field,
                            'type_display': q.get_type_field_display(),
                            'ordering': q.ordering,
                            'required': q.required
                        }
                        for q in s.questions.all().order_by('ordering')
                    ]
                }
                for s in sections
            ],
            'unassigned_questions': [
                {
                    'id': q.id,
                    'label': q.label,
                    'type_field': q.type_field,
                    'type_display': q.get_type_field_display(),
                    'ordering': q.ordering,
                    'required': q.required
                }
                for q in unassigned
            ]
        })


@method_decorator(staff_member_required, name='dispatch')
@method_decorator(csrf_protect, name='dispatch')
class SectionCreateAPIView(View):
    """Create new section."""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            survey = get_object_or_404(Survey, slug=data['survey_slug'])
            
            # Get max ordering
            max_ordering = Section.objects.filter(survey=survey).count()
            
            section = Section.objects.create(
                survey=survey,
                name=data.get('name', 'New Section'),
                description=data.get('description', ''),
                ordering=data.get('ordering', max_ordering)
            )
            
            return JsonResponse({
                'id': section.id,
                'name': section.name,
                'description': section.description,
                'ordering': section.ordering,
                'questions': []
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


@method_decorator(staff_member_required, name='dispatch')
@method_decorator(csrf_protect, name='dispatch')
class SectionUpdateAPIView(View):
    """Update section."""
    
    def patch(self, request, pk):
        try:
            data = json.loads(request.body)
            section = get_object_or_404(Section, pk=pk)
            
            if 'name' in data:
                section.name = data['name']
            if 'description' in data:
                section.description = data['description']
            
            section.save()
            
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


@method_decorator(staff_member_required, name='dispatch')
@method_decorator(csrf_protect, name='dispatch')
class SectionDeleteAPIView(View):
    """Delete section (questions become unassigned)."""
    
    def delete(self, request, pk):
        try:
            section = get_object_or_404(Section, pk=pk)
            section.delete()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


@method_decorator(staff_member_required, name='dispatch')
@method_decorator(csrf_protect, name='dispatch')
class SectionsReorderAPIView(View):
    """Bulk reorder sections."""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            with transaction.atomic():
                for item in data['sections']:
                    Section.objects.filter(pk=item['id']).update(ordering=item['ordering'])
            
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


@method_decorator(staff_member_required, name='dispatch')
@method_decorator(csrf_protect, name='dispatch')
class QuestionMoveAPIView(View):
    """Move question to different section."""
    
    def post(self, request, pk):
        try:
            data = json.loads(request.body)
            question = get_object_or_404(Question, pk=pk)
            
            with transaction.atomic():
                # Update section (null for unassigned)
                section_id = data.get('section_id')
                question.section = Section.objects.get(pk=section_id) if section_id else None
                question.ordering = data.get('ordering', 0)
                question.save()
                
                # Reorder other questions in target section
                if section_id:
                    questions = Question.objects.filter(section_id=section_id).order_by('ordering')
                    for idx, q in enumerate(questions):
                        if q.ordering != idx:
                            q.ordering = idx
                            q.save()
            
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


@method_decorator(staff_member_required, name='dispatch')
@method_decorator(csrf_protect, name='dispatch')
class QuestionDeleteAPIView(View):
    """Delete question via API."""
    
    def delete(self, request, pk):
        try:
            question = get_object_or_404(Question, pk=pk)
            question.delete()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
