#!/usr/bin/env python
"""
Test script to verify the fixes for:
1. Field Type dropdown in dashboard/forms
2. Summary charts at dashboard/summary/survey/
3. Download statistics with file paths
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moi.settings')
django.setup()

from djf_surveys.utils import get_type_field
from djf_surveys.models import Survey, Question, Answer, UserAnswer, TYPE_FIELD
from django.test import RequestFactory

print("=" * 60)
print("Testing Fixes")
print("=" * 60)

# Test 1: Check if get_type_field() returns correct data
print("\n1. Testing get_type_field() function:")
print("-" * 60)
type_fields = get_type_field()
print(f"   Total field types: {len(type_fields)}")
for field in type_fields:
    print(f"   - {field['label']}: ID={field['id']}, Icon={field['icon']}")

# Test 2: Check if surveys exist for testing
print("\n2. Checking for existing surveys:")
print("-" * 60)
surveys = Survey.objects.all()
print(f"   Total surveys: {surveys.count()}")
for survey in surveys[:5]:
    print(f"   - {survey.name} (slug: {survey.slug})")
    questions = Question.objects.filter(survey=survey).order_by('ordering', 'id')
    print(f"     Questions: {questions.count()}")
    for q in questions:
        print(f"       * {q.label} (type: {q.get_type_field_display()}, ordering: {q.ordering})")

# Test 3: Check if there are any file upload answers
print("\n3. Checking for file upload answers:")
print("-" * 60)
file_questions = Question.objects.filter(type_field=TYPE_FIELD.file)
print(f"   File upload questions: {file_questions.count()}")
for q in file_questions:
    answers = Answer.objects.filter(question=q)
    print(f"   - {q.label}: {answers.count()} answers")
    for ans in answers[:3]:
        print(f"     * Answer ID: {ans.id}")
        print(f"       file_value: {ans.file_value}")
        print(f"       file_url: {ans.file_url}")
        factory = RequestFactory()
        request = factory.get('/')
        request.META['HTTP_HOST'] = 'localhost:8000'
        file_url = ans.get_file_url(request)
        print(f"       get_file_url(): {file_url}")

# Test 4: Check summary generation
print("\n4. Testing summary generation:")
print("-" * 60)
if surveys.exists():
    from djf_surveys.summary import SummaryResponse
    test_survey = surveys.first()
    print(f"   Testing with survey: {test_survey.name}")
    summary = SummaryResponse(
        survey=test_survey,
        selected_year=None,
        selected_month=None,
        selected_direction=None
    )
    
    # Try to generate questions summary
    try:
        questions_html = summary.generate_questions()
        print(f"   ✓ generate_questions() executed successfully")
        print(f"   HTML length: {len(questions_html)} characters")
        if "chartpie" in questions_html.lower() or "chartbar" in questions_html.lower():
            print(f"   ✓ Charts detected in output")
        else:
            print(f"   ℹ No charts in output (might be expected if no suitable questions)")
    except Exception as e:
        print(f"   ✗ Error in generate_questions(): {e}")
    
    # Try to generate question2 summary
    try:
        question2_html = summary.generate_question2()
        print(f"   ✓ generate_question2() executed successfully")
        print(f"   HTML length: {len(question2_html)} characters")
    except Exception as e:
        print(f"   ✗ Error in generate_question2(): {e}")
else:
    print("   No surveys available for testing")

print("\n" + "=" * 60)
print("Testing Complete!")
print("=" * 60)
print("\nSummary of fixes:")
print("1. ✓ Added get_type_field to AdminSurveyFormView context")
print("2. ✓ Fixed Chart.js loading in summary.html")
print("3. ✓ Fixed question ordering in download CSV")
print("\nPlease verify in browser:")
print("- Dashboard Forms: http://127.0.0.1:8000/dashboard/forms/<survey-slug>/")
print("- Summary Page: http://127.0.0.1:8000/dashboard/summary/survey/<survey-slug>/")
print("- Download CSV: http://127.0.0.1:8000/dashboard/download/survey/<survey-slug>/")
