"""
Test script for storage backend and branching functionality.

Run with: python3 manage.py shell < test_storage_and_branching.py
Or: python3 test_storage_and_branching.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moi.settings')
django.setup()

from djf_surveys.storage import StorageManager, LocalStorageBackend
from djf_surveys.models import StorageConfiguration, Question, Section, Survey, Answer, UserAnswer
from django.contrib.auth import get_user_model
from io import BytesIO

User = get_user_model()

def test_storage_backend():
    """Test storage backend functionality."""
    print("\n=== Testing Storage Backend ===\n")
    
    # Test LocalStorageBackend
    print("1. Testing LocalStorageBackend...")
    backend = LocalStorageBackend()
    
    # Test connection
    result = backend.test_connection()
    print(f"   Connection test: {result['success']}")
    print(f"   Message: {result['message']}")
    
    # Test save
    test_file = BytesIO(b"Test file content")
    test_file.name = "test.txt"
    path = backend.save(test_file, "test_survey/test_question/test.txt")
    print(f"   File saved to: {path}")
    
    # Test exists
    exists = backend.exists(path)
    print(f"   File exists: {exists}")
    
    # Test get_url
    url = backend.get_url(path)
    print(f"   File URL: {url}")
    
    # Test delete
    deleted = backend.delete(path)
    print(f"   File deleted: {deleted}")
    
    print("   ✅ LocalStorageBackend tests passed!\n")


def test_storage_manager():
    """Test StorageManager."""
    print("=== Testing StorageManager ===\n")
    
    manager = StorageManager()
    
    # Get backend (should default to local)
    backend = manager.get_backend()
    print(f"1. Got backend: {type(backend).__name__}")
    
    # Test connection
    result = manager.test_connection()
    print(f"2. Connection test: {result['success']}")
    
    print("   ✅ StorageManager tests passed!\n")


def test_storage_configuration():
    """Test StorageConfiguration model."""
    print("=== Testing StorageConfiguration Model ===\n")
    
    # Create local storage config
    config = StorageConfiguration.objects.create(
        provider='local',
        config={'base_path': 'survey_uploads'},
        is_active=True
    )
    print(f"1. Created config: {config}")
    
    # Get active config
    active = StorageConfiguration.get_active()
    print(f"2. Active config: {active}")
    
    # Test connection method
    result = config.test_connection()
    print(f"3. Connection test via model: {result['success']}")
    
    # Cleanup
    config.delete()
    print("   ✅ StorageConfiguration tests passed!\n")


def test_question_branching():
    """Test Question branching methods."""
    print("=== Testing Question Branching ===\n")
    
    # Get or create test survey and sections
    try:
        survey = Survey.objects.first()
        if not survey:
            print("   ⚠️  No surveys found. Skipping branching tests.")
            return
        
        sections = Section.objects.filter(survey=survey)[:3]
        if len(sections) < 2:
            print("   ⚠️  Not enough sections. Skipping branching tests.")
            return
        
        # Create test question
        from djf_surveys.models import TYPE_FIELD
        question = Question.objects.create(
            survey=survey,
            section=sections[0],
            label="Test Question with Branching",
            type_field=TYPE_FIELD.radio,
            choices="Yes, No, Maybe",
            enable_branching=True,
            ordering=999
        )
        
        print(f"1. Created test question: {question.id}")
        
        # Set branch targets
        question.set_branch_target("Yes", sections[1].id)
        question.set_branch_target("No", sections[2].id)
        question.set_branch_target("Maybe", 0)  # End survey
        question.save()
        
        print(f"2. Set branch targets:")
        print(f"   'Yes' → Section {sections[1].id}")
        print(f"   'No' → Section {sections[2].id}")
        print(f"   'Maybe' → End survey")
        
        # Test get_branch_target
        target_yes = question.get_branch_target("Yes")
        target_no = question.get_branch_target("No")
        target_maybe = question.get_branch_target("Maybe")
        
        print(f"3. Retrieved branch targets:")
        print(f"   'Yes' → {target_yes}")
        print(f"   'No' → {target_no}")
        print(f"   'Maybe' → {target_maybe}")
        
        # Test has_branching_configured
        has_branching = question.has_branching_configured
        print(f"4. Has branching configured: {has_branching}")
        
        # Cleanup
        question.delete()
        print("   ✅ Question branching tests passed!\n")
        
    except Exception as e:
        print(f"   ❌ Error in branching tests: {e}\n")


def test_answer_file_url():
    """Test Answer.get_file_url() method."""
    print("=== Testing Answer File URL ===\n")
    
    try:
        # Get or create test data
        survey = Survey.objects.first()
        if not survey:
            print("   ⚠️  No surveys found. Skipping Answer tests.")
            return
        
        user = User.objects.first()
        if not user:
            print("   ⚠️  No users found. Skipping Answer tests.")
            return
        
        user_answer = UserAnswer.objects.create(
            survey=survey,
            user=user
        )
        
        from djf_surveys.models import TYPE_FIELD
        question = Question.objects.filter(survey=survey, type_field=TYPE_FIELD.file).first()
        
        if not question:
            # Create file upload question
            question = Question.objects.create(
                survey=survey,
                label="Test File Upload",
                type_field=TYPE_FIELD.file,
                ordering=998
            )
        
        # Create answer with file_url
        answer = Answer.objects.create(
            question=question,
            user_answer=user_answer,
            value="test_file.pdf",
            file_url="https://example.com/files/test_file.pdf"
        )
        
        print(f"1. Created answer with file_url: {answer.file_url}")
        
        # Test get_file_url
        url = answer.get_file_url()
        print(f"2. get_file_url() returned: {url}")
        
        # Test get_value_for_csv
        csv_value = answer.get_value_for_csv
        print(f"3. get_value_for_csv returned: {csv_value}")
        
        # Cleanup
        answer.delete()
        user_answer.delete()
        if question.id == 998 or question.ordering == 998:
            question.delete()
        
        print("   ✅ Answer file URL tests passed!\n")
        
    except Exception as e:
        print(f"   ❌ Error in Answer tests: {e}\n")


def test_branch_evaluator():
    """Test BranchEvaluator with question-level branching."""
    print("=== Testing BranchEvaluator ===\n")
    
    try:
        from djf_surveys.branch_logic import BranchEvaluator
        from djf_surveys.models import TYPE_FIELD
        
        # Get test data
        survey = Survey.objects.first()
        if not survey:
            print("   ⚠️  No surveys found. Skipping BranchEvaluator tests.")
            return
        
        sections = Section.objects.filter(survey=survey).order_by('ordering')[:3]
        if len(sections) < 3:
            print("   ⚠️  Not enough sections. Skipping BranchEvaluator tests.")
            return
        
        # Create question with branching
        question = Question.objects.create(
            survey=survey,
            section=sections[0],
            label="Branch Test Question",
            type_field=TYPE_FIELD.radio,
            choices="Option A, Option B",
            enable_branching=True,
            branch_config={
                'option_a': sections[1].id,
                'option_b': sections[2].id
            },
            ordering=997
        )
        
        print(f"1. Created test question with branching in section {sections[0].id}")
        
        # Test evaluator
        evaluator = BranchEvaluator(sections[0])
        
        # Test with "Option A" answer
        answers = {question.id: "Option A"}
        next_section = evaluator.evaluate(answers)
        
        print(f"2. Evaluated with answer 'Option A':")
        print(f"   Next section: {next_section.id if next_section else 'None'}")
        print(f"   Expected: {sections[1].id}")
        
        # Test with "Option B" answer
        answers = {question.id: "Option B"}
        next_section = evaluator.evaluate(answers)
        
        print(f"3. Evaluated with answer 'Option B':")
        print(f"   Next section: {next_section.id if next_section else 'None'}")
        print(f"   Expected: {sections[2].id}")
        
        # Cleanup
        question.delete()
        print("   ✅ BranchEvaluator tests passed!\n")
        
    except Exception as e:
        print(f"   ❌ Error in BranchEvaluator tests: {e}\n")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("STORAGE AND BRANCHING FUNCTIONALITY TESTS")
    print("="*60)
    
    try:
        test_storage_backend()
        test_storage_manager()
        test_storage_configuration()
        test_question_branching()
        test_answer_file_url()
        test_branch_evaluator()
        
        print("\n" + "="*60)
        print("ALL TESTS COMPLETED!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}\n")
        import traceback
        traceback.print_exc()
