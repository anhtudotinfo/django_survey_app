#!/usr/bin/env python
"""
Test script to create a file upload question
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moi.settings')
django.setup()

from djf_surveys.models import Survey, Section, Question, TYPE_FIELD

# Get or create survey
survey = Survey.objects.first()
if not survey:
    survey = Survey.objects.create(
        name="Test Survey with File Upload",
        description="Testing file upload functionality"
    )
    print(f"Created survey: {survey.name}")
else:
    print(f"Using existing survey: {survey.name}")

# Get or create section
section = survey.sections.first()
if not section:
    section = Section.objects.create(
        survey=survey,
        name="Upload Section",
        description="Test file upload",
        ordering=1
    )
    print(f"Created section: {section.name}")
else:
    print(f"Using existing section: {section.name}")

# Create file upload question
file_question = Question.objects.create(
    survey=survey,
    section=section,
    type_field=TYPE_FIELD.file,
    label="Please upload your CV (PDF or Word)",
    help_text="Accepted formats: PDF, DOC, DOCX. Max size: 10MB",
    required=True,
    ordering=1
)
print(f"\n✓ Created file upload question: {file_question.label}")
print(f"  Type: {file_question.get_type_field_display()}")
print(f"  Required: {file_question.required}")

# Create a text question too for comparison
text_question = Question.objects.create(
    survey=survey,
    section=section,
    type_field=TYPE_FIELD.text,
    label="Your Name",
    help_text="Please enter your full name",
    required=True,
    ordering=0
)
print(f"\n✓ Created text question: {text_question.label}")

print(f"\n✅ Setup complete!")
print(f"Survey URL: /create/{survey.slug}/")
print(f"Total questions in section: {section.questions.count()}")
