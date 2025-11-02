#!/usr/bin/env python3
"""
Test script for branching UI functionality.

This script:
1. Finds or creates a test survey with sections
2. Adds a radio question with branching
3. Verifies the configuration
4. Provides instructions for manual UI testing
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moi.settings')
django.setup()

from djf_surveys.models import Survey, Section, Question, Answer, UserAnswer, TYPE_FIELD
from django.contrib.auth import get_user_model

User = get_user_model()

def test_branching_setup():
    """Set up test survey with branching."""
    print("\n" + "="*60)
    print("BRANCHING UI TEST SETUP")
    print("="*60)
    
    # Use ABC survey which has 3 sections
    survey = Survey.objects.filter(slug='abc').first()
    
    if not survey:
        print("❌ ABC survey not found. Creating...")
        survey = Survey.objects.create(
            name="Branching Test Survey",
            slug="branching-test",
            description="Test survey for section branching"
        )
        
        # Create sections
        Section.objects.create(survey=survey, name="Section A", ordering=0)
        Section.objects.create(survey=survey, name="Section B", ordering=1)
        Section.objects.create(survey=survey, name="Section C", ordering=2)
    
    sections = Section.objects.filter(survey=survey).order_by('ordering')
    print(f"\n✅ Using survey: {survey.name} (ID: {survey.id})")
    print(f"   Slug: {survey.slug}")
    print(f"   Sections ({sections.count()}):")
    for sec in sections:
        print(f"   - {sec.ordering}. {sec.name} (ID: {sec.id})")
    
    # Check for existing radio question
    radio_q = Question.objects.filter(
        survey=survey,
        type_field=TYPE_FIELD.radio
    ).first()
    
    if not radio_q:
        print("\n📝 Creating new radio question...")
        section_a = sections.first()
        radio_q = Question.objects.create(
            survey=survey,
            section=section_a,
            type_field=TYPE_FIELD.radio,
            label="How would you rate your experience?",
            choices="Excellent,Good,Poor",
            help_text="Select one option",
            required=True,
            ordering=0
        )
        print(f"   ✅ Created question: {radio_q.label}")
    else:
        print(f"\n✅ Found existing radio question: {radio_q.label}")
    
    print(f"   ID: {radio_q.id}")
    print(f"   Type: {radio_q.get_type_field_display()}")
    print(f"   Choices: {radio_q.choices}")
    print(f"   Branching enabled: {radio_q.enable_branching}")
    
    # Add branching configuration programmatically as example
    if not radio_q.enable_branching:
        print("\n🔧 Enabling branching and setting up example configuration...")
        radio_q.enable_branching = True
        
        # Map choices to sections
        # Excellent -> Section B, Good -> Section C, Poor -> End survey
        if sections.count() >= 2:
            section_b = sections[1]
            section_c = sections[2] if sections.count() >= 3 else sections[1]
            
            radio_q.branch_config = {
                'excellent': section_b.id,  # Jump to Section B
                'good': section_c.id,        # Jump to Section C
                'poor': 0                    # End survey
            }
            radio_q.save()
            
            print(f"   ✅ Branching configured:")
            print(f"      'Excellent' → Section B (ID: {section_b.id})")
            print(f"      'Good' → Section C (ID: {section_c.id})")
            print(f"      'Poor' → End Survey (0)")
    
    return survey, radio_q


def test_branching_evaluation():
    """Test that branching logic works correctly."""
    print("\n" + "="*60)
    print("BRANCHING LOGIC TEST")
    print("="*60)
    
    from djf_surveys.branch_logic import BranchEvaluator
    
    survey = Survey.objects.filter(slug='abc').first()
    if not survey:
        print("❌ Survey not found")
        return
    
    sections = Section.objects.filter(survey=survey).order_by('ordering')
    section_a = sections.first()
    
    radio_q = Question.objects.filter(
        survey=survey,
        type_field=TYPE_FIELD.radio,
        enable_branching=True
    ).first()
    
    if not radio_q:
        print("❌ No radio question with branching found")
        return
    
    print(f"\n✅ Testing question: {radio_q.label}")
    print(f"   Branch config: {radio_q.branch_config}")
    
    # Create evaluator
    evaluator = BranchEvaluator(section_a)
    
    # Test different answers
    test_cases = [
        ('Excellent', 'excellent'),
        ('Good', 'good'),
        ('Poor', 'poor')
    ]
    
    print("\n📊 Testing branch evaluation:")
    for choice, normalized in test_cases:
        answers = {radio_q.id: choice}
        next_section = evaluator.evaluate(answers)
        
        expected_target = radio_q.branch_config.get(normalized)
        
        if expected_target == 0:
            expected_text = "End survey"
        elif expected_target:
            target_sec = Section.objects.get(id=expected_target)
            expected_text = f"{target_sec.name} (ID: {expected_target})"
        else:
            expected_text = "Next section (default)"
        
        actual_text = f"{next_section.name} (ID: {next_section.id})" if next_section else "End survey"
        
        status = "✅" if str(next_section.id if next_section else 0) == str(expected_target) else "❌"
        print(f"   {status} '{choice}' → Expected: {expected_text}, Got: {actual_text}")


def print_testing_instructions():
    """Print manual testing instructions."""
    print("\n" + "="*60)
    print("MANUAL UI TESTING INSTRUCTIONS")
    print("="*60)
    
    survey = Survey.objects.filter(slug='abc').first()
    
    print(f"""
🌐 Server: http://localhost:8000

📋 Test Steps:

1. Navigate to Admin:
   http://localhost:8000/dashboard/

2. Go to Survey Manager:
   http://localhost:8000/dashboard/surveys/{survey.slug}/

3. Find the radio question and click "Edit" (pencil icon)

4. Verify the Branching UI:
   ✅ Purple/blue "Section Branching" panel should appear
   ✅ "Enable section branching" checkbox should be checked
   ✅ Each choice should have a dropdown:
      - Excellent → Section B
      - Good → Section C
      - Poor → End survey
   ✅ Preview section should show the branching flow

5. Test Editing:
   - Change one of the targets
   - Verify preview updates
   - Save and reload - verify changes persist

6. Test Survey Navigation:
   - Go to: http://localhost:8000/surveys/{survey.slug}/
   - Answer the radio question with different choices
   - Verify navigation goes to correct section:
     * "Excellent" should jump to Section B
     * "Good" should jump to Section C
     * "Poor" should end the survey

7. Test Creating New Question:
   - Create a new radio question
   - Select "Radio" type
   - Add choices
   - Verify branching panel appears
   - Enable branching and configure
   - Save and test

📸 Visual Checks:
   ✅ Gradient purple/blue background
   ✅ Icons (🔀 for title, numbered circles for choices)
   ✅ Dropdowns with emoji options (➡️ 🏁 📍)
   ✅ Color-coded preview (gray/red/purple arrows)
   ✅ Smooth transitions and updates

🐛 Things to Check:
   - Does branching panel hide for non-radio questions?
   - Does toggle show/hide configuration?
   - Does preview update when choices change?
   - Does configuration persist after save?
   - Does actual navigation work correctly?

""")


if __name__ == "__main__":
    print("\n🧪 Starting Branching UI Tests...\n")
    
    try:
        # Setup test data
        survey, question = test_branching_setup()
        
        # Test branching logic
        test_branching_evaluation()
        
        # Print instructions
        print_testing_instructions()
        
        print("\n" + "="*60)
        print("✅ TEST SETUP COMPLETE!")
        print("="*60)
        print("\nThe survey is ready for manual testing.")
        print("Follow the instructions above to test the UI.\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
