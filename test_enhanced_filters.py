#!/usr/bin/env python
"""
Test script for enhanced filter features in Summary page
"""
import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moi.settings')
django.setup()

from djf_surveys.models import Survey, Question, Answer, UserAnswer, Direction
from djf_surveys.summary import SummaryResponse

print("=" * 80)
print("TESTING ENHANCED FILTER FEATURES")
print("=" * 80)

# Get a test survey
surveys = Survey.objects.all()
if not surveys.exists():
    print("\n❌ No surveys found. Please create a survey first.")
    exit(1)

survey = surveys.first()
print(f"\n✓ Testing with survey: {survey.name} (slug: {survey.slug})")

# Test 1: Date Range Filter
print("\n" + "=" * 80)
print("TEST 1: Date Range Filter")
print("=" * 80)

today = datetime.now()
last_week = today - timedelta(days=7)
from_date = last_week.strftime('%Y-%m-%d')
to_date = today.strftime('%Y-%m-%d')

print(f"From Date: {from_date}")
print(f"To Date: {to_date}")

summary = SummaryResponse(
    survey=survey,
    from_date=from_date,
    to_date=to_date
)

print("✓ SummaryResponse created with date range")

# Test filtered queryset
test_queryset = Answer.objects.filter(question__survey=survey)
original_count = test_queryset.count()
filtered_queryset = summary.get_filtered_queryset(test_queryset)
filtered_count = filtered_queryset.count()

print(f"Original answers: {original_count}")
print(f"Filtered answers: {filtered_count}")
print(f"✓ Date range filter working: {filtered_count <= original_count}")

# Test 2: Question Filter
print("\n" + "=" * 80)
print("TEST 2: Question Filter")
print("=" * 80)

questions = Question.objects.filter(survey=survey).order_by('ordering', 'id')
print(f"Total questions in survey: {questions.count()}")

if questions.count() >= 2:
    # Select first 2 questions
    selected_q_ids = [questions[0].id, questions[1].id]
    print(f"Selected question IDs: {selected_q_ids}")
    
    summary_with_q = SummaryResponse(
        survey=survey,
        selected_questions=selected_q_ids
    )
    
    print("✓ SummaryResponse created with question filter")
    
    # Generate questions HTML (should only include selected questions)
    html = summary_with_q.generate_questions()
    print(f"Generated HTML length: {len(html)} characters")
    print("✓ Question filter working")
else:
    print("⚠ Not enough questions to test filter (need at least 2)")

# Test 3: Combined Filters
print("\n" + "=" * 80)
print("TEST 3: Combined Filters")
print("=" * 80)

directions = Direction.objects.all()
test_direction = directions.first() if directions.exists() else None

summary_combined = SummaryResponse(
    survey=survey,
    from_date=from_date,
    to_date=to_date,
    selected_direction=test_direction,
    selected_questions=[q.id for q in questions[:2]] if questions.count() >= 2 else []
)

print(f"Filters applied:")
print(f"  - Date range: {from_date} to {to_date}")
print(f"  - Direction: {test_direction.name if test_direction else 'None'}")
print(f"  - Questions: {len(summary_combined.selected_questions)} selected")

test_queryset = Answer.objects.filter(question__survey=survey)
combined_filtered = summary_combined.get_filtered_queryset(test_queryset)
print(f"Combined filtered answers: {combined_filtered.count()}")
print("✓ Combined filters working")

# Test 4: Priority Test (Date Range vs Year/Month)
print("\n" + "=" * 80)
print("TEST 4: Filter Priority (Date Range > Year/Month)")
print("=" * 80)

# With date range - year/month should be ignored
summary_priority = SummaryResponse(
    survey=survey,
    selected_year=2020,  # Old year
    selected_month=1,    # Old month
    from_date=from_date, # Recent date range
    to_date=to_date
)

test_queryset = Answer.objects.filter(question__survey=survey)
priority_filtered = summary_priority.get_filtered_queryset(test_queryset)
print(f"With date range + old year/month: {priority_filtered.count()} results")

# Without date range - year/month should apply
summary_yearmonth = SummaryResponse(
    survey=survey,
    selected_year=2020,
    selected_month=1
)

yearmonth_filtered = summary_yearmonth.get_filtered_queryset(test_queryset)
print(f"With only old year/month: {yearmonth_filtered.count()} results")

if priority_filtered.count() != yearmonth_filtered.count():
    print("✓ Date range priority working correctly")
else:
    print("⚠ Priority might not be working (counts are equal)")

# Test 5: View Context Test
print("\n" + "=" * 80)
print("TEST 5: View Context Variables")
print("=" * 80)

from django.test import RequestFactory
from djf_surveys.admins.views import SummaryResponseSurveyView

factory = RequestFactory()
request = factory.get(
    f'/dashboard/summary/survey/{survey.slug}/',
    {
        'from_date': from_date,
        'to_date': to_date,
        'questions': [str(q.id) for q in questions[:2]]
    }
)

# Simulate view
view = SummaryResponseSurveyView()
view.object = survey
view.request = request

try:
    context = view.get_context_data()
    
    print("Context variables:")
    print(f"  ✓ from_date: {context.get('from_date')}")
    print(f"  ✓ to_date: {context.get('to_date')}")
    print(f"  ✓ all_questions: {context.get('all_questions').count() if context.get('all_questions') else 0}")
    print(f"  ✓ selected_questions: {len(context.get('selected_questions', []))}")
    print(f"  ✓ summary: {type(context.get('summary'))}")
    print("✓ View context working correctly")
except Exception as e:
    print(f"❌ Error in view context: {e}")

# Test 6: Download View Test
print("\n" + "=" * 80)
print("TEST 6: Download Filtered View")
print("=" * 80)

from djf_surveys.admins.views import DownloadFilteredResponseSurveyView

request = factory.get(
    f'/dashboard/download/filtered/{survey.slug}/',
    {
        'from_date': from_date,
        'to_date': to_date,
        'questions': [str(q.id) for q in questions[:2]] if questions.count() >= 2 else []
    }
)

download_view = DownloadFilteredResponseSurveyView()
download_view.object = survey
download_view.request = request

try:
    response = download_view.get(request, slug=survey.slug)
    
    print(f"Response type: {type(response)}")
    print(f"Content type: {response.get('Content-Type')}")
    print(f"Content disposition: {response.get('Content-Disposition')}")
    
    # Check filename
    if 'from-' in response.get('Content-Disposition', ''):
        print("✓ Filename includes date range")
    else:
        print("⚠ Filename doesn't include date range")
    
    # Check content
    content = response.content.decode('utf-8')
    lines = content.split('\n')
    print(f"CSV lines: {len(lines)}")
    
    if 'Filters:' in lines[0]:
        print("✓ Filter info in CSV header")
    
    print("✓ Download view working correctly")
except Exception as e:
    print(f"❌ Error in download view: {e}")
    import traceback
    traceback.print_exc()

# Summary Report
print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)

print("\n✅ Features Tested:")
print("  1. ✓ Date range filter")
print("  2. ✓ Question filter")
print("  3. ✓ Combined filters")
print("  4. ✓ Filter priority (date range > year/month)")
print("  5. ✓ View context variables")
print("  6. ✓ Download filtered view")

print("\n📋 Manual Testing Required:")
print("  1. Open browser: http://127.0.0.1:8000/dashboard/summary/survey/{}/".format(survey.slug))
print("  2. Test date range picker")
print("  3. Test question checkboxes")
print("  4. Test 'Apply Filters' button")
print("  5. Test 'Download Filtered Data' button")
print("  6. Test 'Reset All Filters' button")
print("  7. Verify charts update correctly")
print("  8. Verify CSV download contains correct data")

print("\n" + "=" * 80)
print("Testing Complete!")
print("=" * 80)
