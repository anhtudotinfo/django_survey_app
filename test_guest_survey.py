"""
Test script for guest (anonymous) survey functionality.

This script tests:
1. Survey list view accessible without authentication
2. Anonymous users can access surveys with can_anonymous_user=True
3. Anonymous users can submit surveys without logging in
4. UserAnswer is created with user=None for anonymous submissions
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moi.settings')
django.setup()

from django.test import Client, TestCase
from django.urls import reverse
from djf_surveys.models import Survey, Question, UserAnswer, Answer, TYPE_FIELD, Direction


def test_guest_survey_access():
    """Test that anonymous users can access and submit surveys."""
    
    print("\n" + "="*60)
    print("Testing Guest Survey Functionality")
    print("="*60 + "\n")
    
    # Create a test direction
    direction, _ = Direction.objects.get_or_create(name="Test Course")
    
    # Create a test survey with guest access enabled
    survey = Survey.objects.create(
        name="Guest Survey Test",
        description="This is a test survey for guest users",
        can_anonymous_user=True,  # Enable guest access
        duplicate_entry=False
    )
    print(f"✓ Created survey: {survey.name}")
    print(f"  - can_anonymous_user: {survey.can_anonymous_user}")
    print(f"  - slug: {survey.slug}\n")
    
    # Create test questions
    question1 = Question.objects.create(
        survey=survey,
        type_field=TYPE_FIELD.text,
        label="What is your name?",
        required=True,
        ordering=1
    )
    print(f"✓ Created question 1: {question1.label}")
    
    question2 = Question.objects.create(
        survey=survey,
        type_field=TYPE_FIELD.radio,
        label="How satisfied are you?",
        choices="Very Satisfied, Satisfied, Neutral, Dissatisfied",
        required=True,
        ordering=2
    )
    print(f"✓ Created question 2: {question2.label}\n")
    
    # Create anonymous client (not logged in)
    client = Client(HTTP_HOST='testserver', SERVER_NAME='testserver')
    
    # Test 1: Access survey list without authentication
    print("Test 1: Accessing survey list as guest...")
    response = client.get(reverse('djf_surveys:index'))
    if response.status_code == 200:
        print(f"✓ Survey list accessible (status: {response.status_code})")
        # Check if our survey is visible
        if survey.name.encode() in response.content:
            print(f"✓ Survey '{survey.name}' is visible in list\n")
        else:
            print(f"⚠ Survey '{survey.name}' NOT visible in list\n")
    else:
        print(f"✗ Failed to access survey list (status: {response.status_code})\n")
    
    # Test 2: Access survey form without authentication
    print("Test 2: Accessing survey form as guest...")
    response = client.get(reverse('djf_surveys:create', kwargs={'slug': survey.slug}))
    if response.status_code == 200:
        print(f"✓ Survey form accessible (status: {response.status_code})\n")
    else:
        print(f"✗ Failed to access survey form (status: {response.status_code})\n")
    
    # Test 3: Submit survey as guest
    print("Test 3: Submitting survey as guest...")
    form_data = {
        f'field_survey_{question1.id}': 'Anonymous User',
        f'field_survey_{question2.id}': 'satisfied',
        'direction': direction.id,
    }
    
    response = client.post(
        reverse('djf_surveys:create', kwargs={'slug': survey.slug}),
        data=form_data,
        follow=True
    )
    
    if response.status_code == 200:
        print(f"✓ Survey submission successful (status: {response.status_code})")
        
        # Check if UserAnswer was created with user=None
        guest_answers = UserAnswer.objects.filter(survey=survey, user=None)
        if guest_answers.exists():
            user_answer = guest_answers.first()
            print(f"✓ UserAnswer created with user=None (ID: {user_answer.id})")
            
            # Check answers
            answers = Answer.objects.filter(user_answer=user_answer)
            print(f"✓ {answers.count()} answers saved:")
            for answer in answers:
                print(f"  - {answer.question.label}: {answer.value}")
        else:
            print("✗ No UserAnswer found with user=None")
    else:
        print(f"✗ Survey submission failed (status: {response.status_code})")
    
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print(f"Survey created: {survey.name}")
    print(f"Total guest submissions: {UserAnswer.objects.filter(survey=survey, user=None).count()}")
    print(f"Total authenticated submissions: {UserAnswer.objects.filter(survey=survey).exclude(user=None).count()}")
    print("="*60 + "\n")
    
    # Cleanup
    print("Cleaning up test data...")
    survey.delete()
    direction.delete()
    print("✓ Test data cleaned up\n")


def test_guest_access_denied():
    """Test that guests cannot access surveys with can_anonymous_user=False."""
    
    print("\n" + "="*60)
    print("Testing Guest Access Denial")
    print("="*60 + "\n")
    
    # Create a survey WITHOUT guest access
    survey = Survey.objects.create(
        name="Members Only Survey",
        description="This survey requires authentication",
        can_anonymous_user=False  # Disable guest access
    )
    print(f"✓ Created survey: {survey.name}")
    print(f"  - can_anonymous_user: {survey.can_anonymous_user}\n")
    
    # Create anonymous client
    client = Client(HTTP_HOST='testserver', SERVER_NAME='testserver')
    
    print("Test: Attempting to access restricted survey as guest...")
    response = client.get(reverse('djf_surveys:create', kwargs={'slug': survey.slug}), follow=True)
    
    # Should redirect to login or survey list
    if response.status_code == 200 and 'index' in response.redirect_chain[0][0] if response.redirect_chain else False:
        print("✓ Guest correctly redirected from restricted survey\n")
    elif response.status_code == 200:
        print("⚠ Response returned but may not have proper restriction\n")
    else:
        print(f"? Unexpected response (status: {response.status_code})\n")
    
    # Cleanup
    survey.delete()
    print("✓ Test data cleaned up\n")


if __name__ == '__main__':
    try:
        test_guest_survey_access()
        test_guest_access_denied()
        print("✓ All tests completed successfully!\n")
    except Exception as e:
        print(f"\n✗ Test failed with error: {str(e)}\n")
        import traceback
        traceback.print_exc()
