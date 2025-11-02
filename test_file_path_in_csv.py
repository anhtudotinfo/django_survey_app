#!/usr/bin/env python
"""
Test script to verify file upload local path in CSV export
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moi.settings')
django.setup()

from djf_surveys.models import Survey, Question, Answer, UserAnswer, TYPE_FIELD
from django.test import RequestFactory
from django.conf import settings

print("=" * 80)
print("TESTING FILE LOCAL PATH IN CSV EXPORT")
print("=" * 80)

# Find surveys with file upload questions
file_questions = Question.objects.filter(type_field=TYPE_FIELD.file)
print(f"\nFound {file_questions.count()} file upload questions")

if file_questions.count() == 0:
    print("⚠ No file upload questions found. Create one first.")
    exit(0)

# Get answers for file questions
print("\n" + "=" * 80)
print("FILE UPLOAD ANSWERS")
print("=" * 80)

factory = RequestFactory()
request = factory.get('/')
request.META['HTTP_HOST'] = 'localhost:8000'
request.META['SERVER_PORT'] = '8000'
request.META['wsgi.url_scheme'] = 'http'

for question in file_questions[:5]:  # Test first 5
    print(f"\n📋 Question: {question.label}")
    print(f"   Survey: {question.survey.name}")
    
    answers = Answer.objects.filter(question=question, file_value__isnull=False).exclude(file_value='')
    print(f"   Answers with files: {answers.count()}")
    
    for answer in answers[:3]:  # Show first 3 answers
        print(f"\n   Answer ID: {answer.id}")
        print(f"   User: {answer.user_answer.user.username if answer.user_answer.user else 'Anonymous'}")
        
        # Test old method (URL only)
        url_only = answer.get_file_url(request)
        print(f"   📎 URL (old): {url_only}")
        
        # Test new method (local path)
        local_path = answer.get_file_local_path()
        print(f"   📁 Local Path (new): {local_path}")
        
        # Check if file exists
        if local_path and os.path.exists(local_path):
            file_size = os.path.getsize(local_path)
            print(f"   ✓ File exists on disk ({file_size} bytes)")
        elif local_path:
            print(f"   ⚠ File path exists but file not found on disk")
        else:
            print(f"   ⚠ No local path available")
        
        # Test combined method (for CSV)
        csv_value = answer.get_file_info_for_csv(request)
        print(f"   📊 CSV Export (combined):")
        print(f"      {csv_value}")

print("\n" + "=" * 80)
print("CSV FORMAT EXAMPLE")
print("=" * 80)

print("\nOld format (URL only):")
print("   user1,2025-11-02,http://127.0.0.1:8000/download/file/80/")

print("\nNew format (URL | Local Path):")
print("   user1,2025-11-02,http://127.0.0.1:8000/download/file/80/ | /path/to/media/survey_uploads/...")

print("\n" + "=" * 80)
print("TESTING DOWNLOAD VIEW INTEGRATION")
print("=" * 80)

# Test with actual survey
if file_questions.exists():
    survey = file_questions.first().survey
    print(f"\nTesting with survey: {survey.name} (slug: {survey.slug})")
    
    user_answers = UserAnswer.objects.filter(survey=survey)[:3]
    print(f"Sample UserAnswers: {user_answers.count()}")
    
    for ua in user_answers:
        print(f"\n  UserAnswer ID: {ua.id}")
        print(f"  User: {ua.user.username if ua.user else 'Anonymous'}")
        
        # Get all answers for this UserAnswer
        file_answers = ua.answer_set.filter(question__type_field=TYPE_FIELD.file)
        if file_answers.exists():
            print(f"  File answers: {file_answers.count()}")
            for fa in file_answers:
                csv_val = fa.get_file_info_for_csv(request)
                print(f"    - {fa.question.label[:50]}: {csv_val[:100]}...")

print("\n" + "=" * 80)
print("MEDIA CONFIGURATION")
print("=" * 80)

print(f"\nMEDIA_ROOT: {settings.MEDIA_ROOT}")
print(f"MEDIA_URL: {settings.MEDIA_URL}")

# Check if MEDIA_ROOT exists
if os.path.exists(settings.MEDIA_ROOT):
    print(f"✓ MEDIA_ROOT directory exists")
    
    # Count files in survey_uploads
    survey_uploads = os.path.join(settings.MEDIA_ROOT, 'survey_uploads')
    if os.path.exists(survey_uploads):
        file_count = 0
        for root, dirs, files in os.walk(survey_uploads):
            file_count += len(files)
        print(f"✓ survey_uploads exists with {file_count} files")
    else:
        print(f"⚠ survey_uploads directory not found")
else:
    print(f"⚠ MEDIA_ROOT directory does not exist")

print("\n" + "=" * 80)
print("BENEFITS OF NEW FORMAT")
print("=" * 80)

print("""
1. ✓ Download URL - for accessing file via web
2. ✓ Local Path - for server-side file management
3. ✓ Easy identification - see exact file location
4. ✓ Backup/Migration - know where files are stored
5. ✓ Debugging - verify file existence on disk

CSV Format:
  URL | Local Path
  
Example:
  http://127.0.0.1:8000/download/file/80/ | /home/user/media/survey_uploads/1/3/document.pdf
""")

print("\n" + "=" * 80)
print("TESTING COMPLETE!")
print("=" * 80)

print("\nNext steps:")
print("1. Download CSV from: http://127.0.0.1:8000/dashboard/download/survey/<slug>/")
print("2. Check file columns - should show: URL | Local Path")
print("3. Verify local paths match actual files on server")
print("4. Test filtered download: http://127.0.0.1:8000/dashboard/download/filtered/<slug>/")
