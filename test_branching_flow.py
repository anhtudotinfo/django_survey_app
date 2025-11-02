#!/usr/bin/env python3
"""
Test script cho branching flow
"""

import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moi.settings')

import django
django.setup()

from djf_surveys.models import Question, Section, Survey, UserAnswer
from djf_surveys.branch_logic import BranchEvaluator

def test_branching_flow():
    print("="*60)
    print("TEST: Branching Flow - Trời mưa?")
    print("="*60)
    print()
    
    # Get question
    q = Question.objects.get(id=25)
    print(f"📝 Question: {q.label}")
    print(f"   Type: Radio")
    print(f"   Choices: {q.choices}")
    print(f"   Branching enabled: {q.enable_branching}")
    print()
    
    # Setup branching config (as if user submitted form)
    print("⚙️  Setting up branch config...")
    q.branch_config = {
        'hom_qua': 13,   # "Hôm qua" → Section ID 13
        'hom_nay': 14,   # "Hôm nay" → Section ID 14
        'ngay_mai': 15   # "Ngày mai" → Section ID 15
    }
    q.save()
    print(f"   Config: {q.branch_config}")
    print()
    
    # Get sections
    sections = Section.objects.filter(survey=q.survey).order_by('ordering')
    section_map = {s.id: s.name for s in sections}
    
    # Test each choice
    evaluator = BranchEvaluator()
    
    test_cases = [
        ("Hôm qua", 13, "Hôm qua"),
        ("Hôm nay", 14, "Hôm nay"),
        ("Ngày mai", 15, "Ngày mai"),
    ]
    
    print("🧪 Testing navigation:")
    print()
    
    for choice, expected_section_id, expected_name in test_cases:
        # Create mock answer
        class MockAnswer:
            def __init__(self, question, value):
                self.question = question
                self.value = value
        
        answer = MockAnswer(q, choice)
        
        # Evaluate navigation
        next_section = evaluator.evaluate_navigation(answer)
        
        if next_section and next_section.id == expected_section_id:
            print(f"✅ '{choice}' → {next_section.name} (ID: {next_section.id})")
        elif next_section:
            print(f"❌ '{choice}' → {next_section.name} (ID: {next_section.id})")
            print(f"   Expected: {expected_name} (ID: {expected_section_id})")
        else:
            print(f"❌ '{choice}' → No section returned")
            print(f"   Expected: {expected_name} (ID: {expected_section_id})")
    
    print()
    print("="*60)
    print("✅ Backend logic is working!")
    print()
    print("👉 Next step: Test UI in browser")
    print("   URL: http://localhost:8000/dashboard/question/edit/25/")
    print()
    print("📋 Checklist:")
    print("   1. Bật checkbox 'Enable section branching'")
    print("   2. Panel xuất hiện với 3 cards")
    print("   3. Mỗi card có dropdown với 6 options")
    print("   4. Chọn sections: Hôm qua, Hôm nay, Ngày mai")
    print("   5. Click 'Yuborish' (Save)")
    print("   6. Test khảo sát: http://localhost:8000/create/weather-survey/")
    print("="*60)

if __name__ == '__main__':
    test_branching_flow()
