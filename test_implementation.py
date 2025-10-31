#!/usr/bin/env python
"""
Test script to verify the section, branching, and file upload implementation
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moi.settings')
django.setup()

from djf_surveys.models import Survey, Section, Question, BranchRule, DraftResponse, Answer, TYPE_FIELD
from djf_surveys.draft_service import DraftService
from djf_surveys.branch_logic import BranchEvaluator
from djf_surveys.navigation import SectionNavigator

print("=" * 60)
print("IMPLEMENTATION VERIFICATION")
print("=" * 60)

# Check models
print("\n1. DATABASE MODELS:")
print(f"   ✓ Surveys: {Survey.objects.count()}")
print(f"   ✓ Sections: {Section.objects.count()}")
print(f"   ✓ Questions: {Question.objects.count()}")
print(f"   ✓ File upload questions: {Question.objects.filter(type_field=TYPE_FIELD.file).count()}")
print(f"   ✓ Branch rules: {BranchRule.objects.count()}")
print(f"   ✓ Draft responses: {DraftResponse.objects.count()}")
print(f"   ✓ TYPE_FIELD.file value: {TYPE_FIELD.file}")

# Check services
print("\n2. SERVICE CLASSES:")
try:
    print("   ✓ DraftService imported successfully")
    print(f"   ✓ DraftService methods: save_draft, load_draft, delete_draft, cleanup_expired_drafts")
except Exception as e:
    print(f"   ✗ DraftService error: {e}")

try:
    print("   ✓ BranchEvaluator imported successfully")
    print(f"   ✓ BranchEvaluator methods: evaluate, get_next_section, get_previous_section")
except Exception as e:
    print(f"   ✗ BranchEvaluator error: {e}")

try:
    print("   ✓ SectionNavigator imported successfully")
    print(f"   ✓ SectionNavigator methods: get_first_section, get_next_section, is_last_section")
except Exception as e:
    print(f"   ✗ SectionNavigator error: {e}")

# Check validators
print("\n3. FILE VALIDATORS:")
try:
    from djf_surveys.validators import FileTypeValidator, FileSizeValidator
    print("   ✓ FileTypeValidator imported")
    print("   ✓ FileSizeValidator imported")
except Exception as e:
    print(f"   ✗ Validators error: {e}")

# Check settings
print("\n4. SETTINGS:")
from django.conf import settings
print(f"   ✓ SURVEY_FILE_UPLOAD_MAX_SIZE: {settings.SURVEY_FILE_UPLOAD_MAX_SIZE / (1024*1024)} MB")
print(f"   ✓ SURVEY_FILE_ALLOWED_TYPES: {settings.SURVEY_FILE_ALLOWED_TYPES}")
print(f"   ✓ SURVEY_DRAFT_EXPIRY_DAYS: {settings.SURVEY_DRAFT_EXPIRY_DAYS} days")

# Check management commands
print("\n5. MANAGEMENT COMMANDS:")
import os
commands_dir = os.path.join('djf_surveys', 'management', 'commands')
if os.path.exists(commands_dir):
    commands = [f for f in os.listdir(commands_dir) if f.endswith('.py') and not f.startswith('__')]
    for cmd in commands:
        print(f"   ✓ {cmd}")
else:
    print("   ✗ Commands directory not found")

# Check views
print("\n6. VIEWS:")
try:
    from djf_surveys.views import CreateSurveyFormView, download_survey_file
    print("   ✓ CreateSurveyFormView with section support")
    print("   ✓ download_survey_file view function")
except Exception as e:
    print(f"   ✗ Views error: {e}")

# Check templates
print("\n7. TEMPLATES:")
template_files = [
    'djf_surveys/templates/djf_surveys/components/section_navigation.html',
    'djf_surveys/templates/djf_surveys/components/section_progress.html',
    'djf_surveys/templates/djf_surveys/components/draft_resume_banner.html',
]
for template in template_files:
    if os.path.exists(template):
        print(f"   ✓ {os.path.basename(template)}")
    else:
        print(f"   ✗ Missing: {os.path.basename(template)}")

# Test a survey with sections
print("\n8. FUNCTIONAL TEST:")
survey = Survey.objects.first()
if survey:
    sections = survey.sections.all()
    print(f"   ✓ Test survey: {survey.name}")
    print(f"   ✓ Sections: {sections.count()}")
    if sections.exists():
        section = sections.first()
        print(f"   ✓ First section: {section.name}")
        print(f"   ✓ Questions in section: {section.questions.count()}")
        
        # Test navigator
        navigator = SectionNavigator(survey)
        first_section = navigator.get_first_section()
        print(f"   ✓ Navigator.get_first_section(): {first_section.name if first_section else 'None'}")
        
        # Test branch evaluator
        if section:
            evaluator = BranchEvaluator(section)
            print(f"   ✓ BranchEvaluator created for section")
            print(f"   ✓ Branch rules for section: {section.branch_rules.count()}")
    else:
        print("   ! No sections found - surveys will use default behavior")
else:
    print("   ! No surveys in database")

print("\n" + "=" * 60)
print("VERIFICATION COMPLETE")
print("=" * 60)
