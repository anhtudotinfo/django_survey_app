#!/usr/bin/env python3
"""
Test script for File Organization functionality
"""

import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moi.settings')
django.setup()

from djf_surveys.models import Survey, UserAnswer, Answer, Question, TYPE_FIELD
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import datetime


def test_file_organization_modes():
    """Test file organization mode settings"""
    print("=" * 60)
    print("TEST 1: File Organization Modes")
    print("=" * 60)
    
    survey = Survey.objects.first()
    if not survey:
        print("❌ No surveys found")
        return False
    
    # Test default mode
    print(f"Default mode: {survey.file_organization}")
    assert survey.file_organization == Survey.FILE_ORG_BY_RESPONSE
    print("✓ Default mode is 'response'")
    
    # Test mode change
    survey.file_organization = Survey.FILE_ORG_BY_QUESTION
    survey.save()
    survey.refresh_from_db()
    assert survey.file_organization == Survey.FILE_ORG_BY_QUESTION
    print("✓ Mode changed to 'question'")
    
    # Reset to default
    survey.file_organization = Survey.FILE_ORG_BY_RESPONSE
    survey.save()
    print("✓ Mode reset to 'response'")
    
    print("✅ File Organization Modes: PASSED\n")
    return True


def test_file_path_generation():
    """Test file path generation with different modes"""
    print("=" * 60)
    print("TEST 2: File Path Generation")
    print("=" * 60)
    
    from djf_surveys.models import upload_survey_file
    
    survey = Survey.objects.first()
    if not survey:
        print("❌ No surveys found")
        return False
    
    # Create test objects
    User = get_user_model()
    user = User.objects.first()
    
    # Create user answer
    user_answer = UserAnswer.objects.create(
        survey=survey,
        user=user
    )
    
    # Create question
    question = Question.objects.create(
        survey=survey,
        label="Upload test file",
        type_field=TYPE_FIELD.file,
        required=False
    )
    
    # Create answer (without saving file yet)
    answer = Answer(
        question=question,
        user_answer=user_answer,
        value="test.pdf"
    )
    
    # Test by-response mode
    survey.file_organization = Survey.FILE_ORG_BY_RESPONSE
    survey.save()
    
    path = upload_survey_file(answer, "test_document.pdf")
    print(f"By Response path: {path}")
    
    expected_parts = ['survey_', 'response_', 'Q']
    for part in expected_parts:
        if part not in path:
            print(f"❌ Missing '{part}' in path")
            return False
    print("✓ By-response path format correct")
    
    # Test by-question mode
    survey.file_organization = Survey.FILE_ORG_BY_QUESTION
    survey.save()
    
    path = upload_survey_file(answer, "test_document.pdf")
    print(f"By Question path: {path}")
    
    expected_parts = ['survey_', 'question_', 'R']
    for part in expected_parts:
        if part not in path:
            print(f"❌ Missing '{part}' in path")
            return False
    print("✓ By-question path format correct")
    
    # Cleanup
    question.delete()
    user_answer.delete()
    survey.file_organization = Survey.FILE_ORG_BY_RESPONSE
    survey.save()
    
    print("✅ File Path Generation: PASSED\n")
    return True


def test_filename_components():
    """Test filename components (prefix, timestamp, original name)"""
    print("=" * 60)
    print("TEST 3: Filename Components")
    print("=" * 60)
    
    from djf_surveys.models import upload_survey_file
    import re
    
    survey = Survey.objects.first()
    if not survey:
        print("❌ No surveys found")
        return False
    
    User = get_user_model()
    user = User.objects.first()
    
    user_answer = UserAnswer.objects.create(survey=survey, user=user)
    question = Question.objects.create(
        survey=survey,
        label="Test",
        type_field=TYPE_FIELD.file,
        required=False
    )
    answer = Answer(question=question, user_answer=user_answer, value="test")
    
    # Generate path
    path = upload_survey_file(answer, "my_document.pdf")
    filename = os.path.basename(path)
    
    print(f"Generated filename: {filename}")
    
    # Check prefix (Q or R)
    if not (filename.startswith('Q') or filename.startswith('R')):
        print("❌ Filename should start with Q or R")
        return False
    print("✓ Has correct prefix (Q or R)")
    
    # Check timestamp pattern (YYYYMMDD_HHMMSS)
    if not re.search(r'\d{8}_\d{6}', filename):
        print("❌ Missing timestamp in format YYYYMMDD_HHMMSS")
        return False
    print("✓ Has timestamp in correct format")
    
    # Check original filename preserved
    if 'my_document' not in filename and 'document' not in filename:
        print("❌ Original filename not preserved")
        return False
    print("✓ Original filename preserved")
    
    # Check extension
    if not filename.endswith('.pdf'):
        print("❌ Extension not preserved")
        return False
    print("✓ Extension preserved")
    
    # Cleanup
    question.delete()
    user_answer.delete()
    
    print("✅ Filename Components: PASSED\n")
    return True


def test_file_statistics():
    """Test file statistics calculation"""
    print("=" * 60)
    print("TEST 4: File Statistics")
    print("=" * 60)
    
    survey = Survey.objects.first()
    if not survey:
        print("❌ No surveys found")
        return False
    
    # Get statistics
    stats = survey.get_file_statistics()
    
    print("File statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Verify structure
    required_keys = ['file_count', 'total_size_bytes', 'total_size_mb', 
                    'organization_type', 'base_folder']
    
    for key in required_keys:
        if key not in stats:
            print(f"❌ Missing key: {key}")
            return False
    
    print("✓ All required keys present")
    
    # Verify types
    assert isinstance(stats['file_count'], int)
    assert isinstance(stats['total_size_bytes'], (int, float))
    assert isinstance(stats['total_size_mb'], (int, float))
    assert isinstance(stats['organization_type'], str)
    assert isinstance(stats['base_folder'], str)
    
    print("✓ All values have correct types")
    
    # Verify base folder format
    if not stats['base_folder'].startswith('survey_'):
        print("❌ Base folder should start with 'survey_'")
        return False
    
    print(f"✓ Base folder format correct: {stats['base_folder']}")
    
    print("✅ File Statistics: PASSED\n")
    return True


def test_get_uploaded_files():
    """Test getting all uploaded files"""
    print("=" * 60)
    print("TEST 5: Get Uploaded Files")
    print("=" * 60)
    
    survey = Survey.objects.first()
    if not survey:
        print("❌ No surveys found")
        return False
    
    # Get uploaded files
    files = survey.get_all_uploaded_files()
    
    print(f"Found {files.count()} uploaded files")
    
    # Verify it's a QuerySet
    from django.db.models import QuerySet
    assert isinstance(files, QuerySet)
    print("✓ Returns QuerySet")
    
    # Verify all files are file type
    for answer in files[:5]:  # Check first 5
        assert answer.question.type_field == TYPE_FIELD.file
        print(f"✓ File: {answer.file_value.name if answer.file_value else 'None'}")
    
    print("✅ Get Uploaded Files: PASSED\n")
    return True


def test_folder_path():
    """Test folder path generation"""
    print("=" * 60)
    print("TEST 6: Folder Path")
    print("=" * 60)
    
    survey = Survey.objects.first()
    if not survey:
        print("❌ No surveys found")
        return False
    
    folder = survey.get_upload_folder_path()
    print(f"Upload folder: {folder}")
    
    # Verify format
    expected_format = f'survey_{survey.id}'
    if folder != expected_format:
        print(f"❌ Expected '{expected_format}', got '{folder}'")
        return False
    
    print("✓ Folder path format correct")
    
    print("✅ Folder Path: PASSED\n")
    return True


def run_all_tests():
    """Run all file organization tests"""
    print("\n" + "=" * 60)
    print("FILE ORGANIZATION TEST SUITE")
    print("=" * 60 + "\n")
    
    results = []
    
    results.append(("File Organization Modes", test_file_organization_modes()))
    results.append(("File Path Generation", test_file_path_generation()))
    results.append(("Filename Components", test_filename_components()))
    results.append(("File Statistics", test_file_statistics()))
    results.append(("Get Uploaded Files", test_get_uploaded_files()))
    results.append(("Folder Path", test_folder_path()))
    
    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All file organization tests passed!")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(run_all_tests())
