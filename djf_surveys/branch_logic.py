"""
Branch logic evaluation for survey navigation.
"""
from typing import Optional, Dict, Any
from django.db.models import QuerySet
from .models import Section, BranchRule, Question


class BranchEvaluator:
    """
    Evaluates branch rules to determine next section based on user answers.
    """
    
    def __init__(self, section: Section):
        self.section = section
        self.rules = section.branch_rules.order_by('priority').select_related(
            'condition_question', 'next_section'
        )
    
    def evaluate(self, answers: Dict[int, Any]) -> Optional[Section]:
        """
        Evaluate branch rules against provided answers.
        
        Priority: Question-level branching > Section-level rules > Sequential next
        
        Args:
            answers: Dict mapping question_id to answer value
            
        Returns:
            Next Section object if rule matches, None if no match or end survey
        """
        # First, check for question-level branching in this section
        # Question-level branching takes precedence over section rules
        next_section = self._evaluate_question_branching(answers)
        if next_section is not False:  # False means no question branching, None means end survey
            return next_section
        
        # Fall back to section-level branch rules
        for rule in self.rules:
            if self._evaluate_rule(rule, answers):
                return rule.next_section  # Can be None (end survey)
        
        # No matching rule, return None (caller should use sequential next)
        return None
    
    def _evaluate_question_branching(self, answers: Dict[int, Any]):
        """
        Check if any radio questions in this section have branching configured.
        
        Args:
            answers: Dict mapping question_id to answer value
            
        Returns:
            Section object to navigate to, None to end survey, or False if no question branching
        """
        from .models import TYPE_FIELD  # Import here to avoid circular imports
        
        # Get all radio questions in this section with branching enabled
        questions_with_branching = Question.objects.filter(
            section=self.section,
            enable_branching=True,
            type_field=TYPE_FIELD.radio  # Only radio questions support branching
        )
        
        for question in questions_with_branching:
            if question.id in answers:
                answer_value = answers[question.id]
                target_section_id = question.get_branch_target(answer_value)
                
                if target_section_id is not None:
                    # Found a branching target
                    if target_section_id == 0 or target_section_id == '':
                        # Special case: end survey
                        return None
                    
                    # Get the target section
                    try:
                        target_section = Section.objects.get(
                            id=target_section_id,
                            survey=self.section.survey
                        )
                        return target_section
                    except Section.DoesNotExist:
                        # Invalid target, log and continue
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.warning(
                            f"Question {question.id} has invalid branch target: {target_section_id}"
                        )
                        continue
        
        # No question-level branching found
        return False
    
    def _evaluate_rule(self, rule: BranchRule, answers: Dict[int, Any]) -> bool:
        """
        Evaluate single rule against answers.
        
        Args:
            rule: BranchRule to evaluate
            answers: User answers dict
            
        Returns:
            True if rule condition matches, False otherwise
        """
        question_id = rule.condition_question.id
        
        # Check if question was answered
        if question_id not in answers:
            return False
        
        user_answer = answers[question_id]
        condition_value = rule.condition_value
        operator = rule.condition_operator
        
        # Evaluate based on operator
        if operator == 'equals':
            return self._normalize_value(user_answer) == self._normalize_value(condition_value)
        
        elif operator == 'not_equals':
            return self._normalize_value(user_answer) != self._normalize_value(condition_value)
        
        elif operator == 'contains':
            # For text fields and multi_select
            user_str = str(user_answer).lower()
            condition_str = str(condition_value).lower()
            return condition_str in user_str
        
        elif operator == 'in':
            # Check if answer is in comma-separated list
            condition_list = [v.strip().lower() for v in condition_value.split(',')]
            user_str = str(user_answer).lower().strip()
            return user_str in condition_list
        
        return False
    
    def _normalize_value(self, value: Any) -> str:
        """
        Normalize value for comparison (case-insensitive, trimmed).
        
        Args:
            value: Value to normalize
            
        Returns:
            Normalized string value
        """
        return str(value).strip().lower()
    
    @staticmethod
    def get_next_section_sequential(current_section: Section) -> Optional[Section]:
        """
        Get next section in sequential order.
        
        Args:
            current_section: Current section
            
        Returns:
            Next section or None if current is last
        """
        return Section.objects.filter(
            survey=current_section.survey,
            ordering__gt=current_section.ordering
        ).order_by('ordering').first()
    
    @staticmethod
    def get_previous_section(current_section: Section) -> Optional[Section]:
        """
        Get previous section in sequential order.
        
        Args:
            current_section: Current section
            
        Returns:
            Previous section or None if current is first
        """
        return Section.objects.filter(
            survey=current_section.survey,
            ordering__lt=current_section.ordering
        ).order_by('-ordering').first()
    
    @staticmethod
    def get_first_section(survey) -> Optional[Section]:
        """
        Get first section of survey.
        
        Args:
            survey: Survey object
            
        Returns:
            First section or None if no sections
        """
        return Section.objects.filter(survey=survey).order_by('ordering').first()
