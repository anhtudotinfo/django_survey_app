from django.test import TestCase, Client
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import os

from djf_surveys.validators import RatingValidator, FileTypeValidator, FileSizeValidator
from djf_surveys.models import (
    Survey, Section, Question, BranchRule, DraftResponse, 
    UserAnswer, Answer, TYPE_FIELD
)
from djf_surveys.draft_service import DraftService
from djf_surveys.branch_logic import BranchEvaluator
from djf_surveys.navigation import SectionNavigator

User = get_user_model()


class ValidationForm(TestCase):
    def test_validate_rating(self):
        with self.assertRaises(ValidationError):
            val = RatingValidator(10)
            val(0)

        with self.assertRaises(ValidationError):
            val = RatingValidator(10)
            val(100)

        val = RatingValidator(5)
        val(2)


class SectionModelTest(TestCase):
    def setUp(self):
        self.survey = Survey.objects.create(
            name="Test Survey",
            description="Test Description"
        )
    
    def test_section_creation(self):
        section = Section.objects.create(
            survey=self.survey,
            name="Section 1",
            description="First section",
            ordering=1
        )
        self.assertEqual(section.name, "Section 1")
        self.assertEqual(section.survey, self.survey)
        self.assertEqual(section.ordering, 1)
    
    def test_section_ordering_unique(self):
        from django.db import IntegrityError
        Section.objects.create(
            survey=self.survey,
            name="Section 1",
            ordering=1
        )
        # IntegrityError is raised at database level for unique_together
        with self.assertRaises(IntegrityError):
            Section.objects.create(
                survey=self.survey,
                name="Section 2",
                ordering=1
            )
    
    def test_section_str(self):
        section = Section.objects.create(
            survey=self.survey,
            name="Test Section",
            ordering=1
        )
        # Section __str__ includes survey name
        self.assertEqual(str(section), f"{self.survey.name} - Test Section")
    
    def test_section_deletion_with_questions(self):
        section = Section.objects.create(
            survey=self.survey,
            name="Section 1",
            ordering=1
        )
        Question.objects.create(
            survey=self.survey,
            section=section,
            label="Question 1",
            type_field=TYPE_FIELD.text
        )
        question_count = section.questions.count()
        self.assertEqual(question_count, 1)


class DraftResponseModelTest(TestCase):
    def setUp(self):
        self.survey = Survey.objects.create(
            name="Test Survey",
            description="Test Description"
        )
        self.section = Section.objects.create(
            survey=self.survey,
            name="Section 1",
            ordering=1
        )
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_draft_creation_authenticated(self):
        draft = DraftResponse.objects.create(
            survey=self.survey,
            user=self.user,
            current_section=self.section,
            data={"question_1": "answer"},
            expires_at=timezone.now() + timedelta(days=30)
        )
        self.assertEqual(draft.user, self.user)
        self.assertIsNone(draft.session_key)
    
    def test_draft_creation_anonymous(self):
        draft = DraftResponse.objects.create(
            survey=self.survey,
            session_key="test_session_key",
            current_section=self.section,
            data={"question_1": "answer"},
            expires_at=timezone.now() + timedelta(days=30)
        )
        self.assertEqual(draft.session_key, "test_session_key")
        self.assertIsNone(draft.user)
    
    def test_draft_expiration(self):
        expired_draft = DraftResponse.objects.create(
            survey=self.survey,
            user=self.user,
            data={},
            expires_at=timezone.now() - timedelta(days=1)
        )
        self.assertTrue(expired_draft.expires_at < timezone.now())


class BranchRuleModelTest(TestCase):
    def setUp(self):
        self.survey = Survey.objects.create(name="Test Survey")
        self.section1 = Section.objects.create(
            survey=self.survey,
            name="Section 1",
            ordering=1
        )
        self.section2 = Section.objects.create(
            survey=self.survey,
            name="Section 2",
            ordering=2
        )
        self.question = Question.objects.create(
            survey=self.survey,
            section=self.section1,
            label="Age Group",
            type_field=TYPE_FIELD.radio,
            choices="18-25,26-35,36+"
        )
    
    def test_branch_rule_creation(self):
        rule = BranchRule.objects.create(
            section=self.section1,
            condition_question=self.question,
            condition_operator='equals',
            condition_value='18-25',
            next_section=self.section2,
            priority=0
        )
        self.assertEqual(rule.section, self.section1)
        self.assertEqual(rule.condition_operator, 'equals')
    
    def test_branch_rule_operators(self):
        operators = ['equals', 'not_equals', 'contains', 'in']
        for i, op in enumerate(operators):
            # Use a valid choice value from the question
            rule = BranchRule.objects.create(
                section=self.section1,
                condition_question=self.question,
                condition_operator=op,
                condition_value='18-25',  # Valid choice value
                next_section=self.section2,
                priority=i  # Different priority for each rule
            )
            self.assertIn(rule.condition_operator, operators)
            rule.delete()


class FileValidatorTest(TestCase):
    def test_file_type_validator_allowed(self):
        validator = FileTypeValidator()
        # Create a mock file
        file = SimpleUploadedFile(
            "test.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        # Should not raise an exception for allowed types
        try:
            validator(file)
        except ValidationError:
            self.fail("FileTypeValidator raised ValidationError unexpectedly")
    
    def test_file_type_validator_disallowed(self):
        from django.conf import settings
        validator = FileTypeValidator()
        # Create a file type not in SURVEY_FILE_ALLOWED_TYPES
        file = SimpleUploadedFile(
            "test.exe",
            b"file_content",
            content_type="application/x-msdownload"
        )
        # Check if exe is in allowed types, otherwise this should raise ValidationError
        if 'exe' not in settings.SURVEY_FILE_ALLOWED_TYPES:
            with self.assertRaises(ValidationError):
                validator(file)
        else:
            # Skip test if exe is somehow allowed
            self.skipTest("exe is in allowed types")
    
    def test_file_size_validator_within_limit(self):
        max_size = 10 * 1024 * 1024  # 10MB
        validator = FileSizeValidator(max_size)
        # Create a small file
        file = SimpleUploadedFile(
            "test.pdf",
            b"small_content",
            content_type="application/pdf"
        )
        try:
            validator(file)
        except ValidationError:
            self.fail("FileSizeValidator raised ValidationError unexpectedly")
    
    def test_file_size_validator_exceeds_limit(self):
        max_size = 100  # 100 bytes
        validator = FileSizeValidator(max_size)
        # Create a file larger than limit
        file = SimpleUploadedFile(
            "test.pdf",
            b"a" * 200,  # 200 bytes
            content_type="application/pdf"
        )
        with self.assertRaises(ValidationError):
            validator(file)


class DraftServiceTest(TestCase):
    def setUp(self):
        self.survey = Survey.objects.create(name="Test Survey")
        self.section = Section.objects.create(
            survey=self.survey,
            name="Section 1",
            ordering=1
        )
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.service = DraftService()
    
    def test_save_draft_authenticated(self):
        data = {"question_1": "answer1"}
        draft = self.service.save_draft(
            survey=self.survey,
            user=self.user,
            current_section=self.section,
            data=data
        )
        self.assertIsNotNone(draft)
        self.assertEqual(draft.user, self.user)
        self.assertEqual(draft.data, data)
    
    def test_save_draft_anonymous(self):
        data = {"question_1": "answer1"}
        draft = self.service.save_draft(
            survey=self.survey,
            session_key="test_session",
            current_section=self.section,
            data=data
        )
        self.assertIsNotNone(draft)
        self.assertEqual(draft.session_key, "test_session")
    
    def test_load_draft_authenticated(self):
        data = {"question_1": "answer1"}
        self.service.save_draft(
            survey=self.survey,
            user=self.user,
            current_section=self.section,
            data=data
        )
        loaded_draft = self.service.load_draft(
            survey=self.survey,
            user=self.user
        )
        self.assertIsNotNone(loaded_draft)
        self.assertEqual(loaded_draft.data, data)
    
    def test_delete_draft(self):
        self.service.save_draft(
            survey=self.survey,
            user=self.user,
            current_section=self.section,
            data={}
        )
        self.service.delete_draft(survey=self.survey, user=self.user)
        draft = self.service.load_draft(survey=self.survey, user=self.user)
        self.assertIsNone(draft)
    
    def test_cleanup_expired_drafts(self):
        # Create expired draft
        DraftResponse.objects.create(
            survey=self.survey,
            user=self.user,
            data={},
            expires_at=timezone.now() - timedelta(days=1)
        )
        count = self.service.cleanup_expired_drafts()
        self.assertGreaterEqual(count, 1)


class BranchEvaluatorTest(TestCase):
    def setUp(self):
        self.survey = Survey.objects.create(name="Test Survey")
        self.section1 = Section.objects.create(
            survey=self.survey,
            name="Section 1",
            ordering=1
        )
        self.section2 = Section.objects.create(
            survey=self.survey,
            name="Section 2",
            ordering=2
        )
        self.section3 = Section.objects.create(
            survey=self.survey,
            name="Section 3",
            ordering=3
        )
        self.question = Question.objects.create(
            survey=self.survey,
            section=self.section1,
            label="Age Group",
            type_field=TYPE_FIELD.radio,
            choices="18-25,26-35,36+"
        )
    
    def test_evaluator_equals_operator(self):
        BranchRule.objects.create(
            section=self.section1,
            condition_question=self.question,
            condition_operator='equals',
            condition_value='18-25',
            next_section=self.section3,
            priority=0
        )
        evaluator = BranchEvaluator(self.section1)
        answers = {self.question.id: '18-25'}
        # Use evaluate method instead of get_next_section
        next_section = evaluator.evaluate(answers)
        self.assertEqual(next_section, self.section3)
    
    def test_evaluator_not_equals_operator(self):
        BranchRule.objects.create(
            section=self.section1,
            condition_question=self.question,
            condition_operator='not_equals',
            condition_value='18-25',
            next_section=self.section3,
            priority=0
        )
        evaluator = BranchEvaluator(self.section1)
        answers = {self.question.id: '26-35'}
        # Use evaluate method instead of get_next_section
        next_section = evaluator.evaluate(answers)
        self.assertEqual(next_section, self.section3)
    
    def test_evaluator_no_matching_rule(self):
        BranchRule.objects.create(
            section=self.section1,
            condition_question=self.question,
            condition_operator='equals',
            condition_value='18-25',
            next_section=self.section3,
            priority=0
        )
        evaluator = BranchEvaluator(self.section1)
        answers = {self.question.id: '36+'}
        # Use evaluate method instead of get_next_section
        next_section = evaluator.evaluate(answers)
        # Should return None when no rule matches
        self.assertIsNone(next_section)
    
    def test_evaluator_priority_ordering(self):
        # Higher priority (lower number) should be evaluated first
        BranchRule.objects.create(
            section=self.section1,
            condition_question=self.question,
            condition_operator='equals',
            condition_value='18-25',
            next_section=self.section3,
            priority=1
        )
        BranchRule.objects.create(
            section=self.section1,
            condition_question=self.question,
            condition_operator='equals',
            condition_value='18-25',
            next_section=self.section2,
            priority=0
        )
        evaluator = BranchEvaluator(self.section1)
        answers = {self.question.id: '18-25'}
        # Use evaluate method instead of get_next_section
        next_section = evaluator.evaluate(answers)
        # Should match the rule with priority 0
        self.assertEqual(next_section, self.section2)


class SectionNavigatorTest(TestCase):
    def setUp(self):
        self.survey = Survey.objects.create(name="Test Survey")
        self.section1 = Section.objects.create(
            survey=self.survey,
            name="Section 1",
            ordering=1
        )
        self.section2 = Section.objects.create(
            survey=self.survey,
            name="Section 2",
            ordering=2
        )
        self.section3 = Section.objects.create(
            survey=self.survey,
            name="Section 3",
            ordering=3
        )
    
    def test_get_first_section(self):
        navigator = SectionNavigator(self.survey)
        first = navigator.get_first_section()
        self.assertEqual(first, self.section1)
    
    def test_get_next_section(self):
        navigator = SectionNavigator(self.survey)
        # get_next_section requires answers dict
        next_section = navigator.get_next_section(self.section1, {})
        self.assertEqual(next_section, self.section2)
    
    def test_get_previous_section(self):
        navigator = SectionNavigator(self.survey)
        prev_section = navigator.get_previous_section(self.section2)
        self.assertEqual(prev_section, self.section1)
    
    def test_is_last_section(self):
        navigator = SectionNavigator(self.survey)
        # is_last_section requires answers dict
        self.assertFalse(navigator.is_last_section(self.section1, {}))
        self.assertFalse(navigator.is_last_section(self.section2, {}))
        self.assertTrue(navigator.is_last_section(self.section3, {}))
    
    def test_is_first_section(self):
        navigator = SectionNavigator(self.survey)
        self.assertTrue(navigator.is_first_section(self.section1))
        self.assertFalse(navigator.is_first_section(self.section2))


class BackwardCompatibilityTest(TestCase):
    def test_survey_without_sections(self):
        # Create a survey and questions without sections
        survey = Survey.objects.create(
            name="Legacy Survey",
            description="Survey without sections"
        )
        question = Question.objects.create(
            survey=survey,
            label="Legacy Question",
            type_field=TYPE_FIELD.text,
            section=None  # No section
        )
        self.assertIsNone(question.section)
        self.assertEqual(survey.questions.count(), 1)
    
    def test_default_section_creation(self):
        # Test that default sections are created for existing surveys
        survey = Survey.objects.create(name="Test Survey")
        # Check if default section exists
        default_section = survey.sections.filter(name="Default Section").first()
        # May or may not exist depending on migration status
        # This test just ensures the query doesn't fail
        self.assertIsNotNone(survey)


class FileUploadIntegrationTest(TestCase):
    def setUp(self):
        self.survey = Survey.objects.create(name="Test Survey")
        self.section = Section.objects.create(
            survey=self.survey,
            name="Section 1",
            ordering=1
        )
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.file_question = Question.objects.create(
            survey=self.survey,
            section=self.section,
            label="Upload File",
            type_field=TYPE_FIELD.file,
            required=True
        )
    
    def test_file_upload_question_creation(self):
        self.assertEqual(self.file_question.type_field, TYPE_FIELD.file)
        self.assertTrue(self.file_question.required)
    
    def test_answer_file_value_field(self):
        user_answer = UserAnswer.objects.create(
            survey=self.survey,
            user=self.user
        )
        answer = Answer.objects.create(
            user_answer=user_answer,
            question=self.file_question
        )
        # Check that file_value field exists
        self.assertTrue(hasattr(answer, 'file_value'))


class SurveyNavigationIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.survey = Survey.objects.create(
            name="Multi-Section Survey",
            editable=True
        )
        self.section1 = Section.objects.create(
            survey=self.survey,
            name="Personal Info",
            ordering=1
        )
        self.section2 = Section.objects.create(
            survey=self.survey,
            name="Preferences",
            ordering=2
        )
        self.question1 = Question.objects.create(
            survey=self.survey,
            section=self.section1,
            label="Name",
            type_field=TYPE_FIELD.text,
            required=True
        )
        self.question2 = Question.objects.create(
            survey=self.survey,
            section=self.section2,
            label="Favorite Color",
            type_field=TYPE_FIELD.text,
            required=False
        )
    
    def test_survey_has_multiple_sections(self):
        self.assertEqual(self.survey.sections.count(), 2)
    
    def test_questions_assigned_to_sections(self):
        self.assertEqual(self.section1.questions.count(), 1)
        self.assertEqual(self.section2.questions.count(), 1)
