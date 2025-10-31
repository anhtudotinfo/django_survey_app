"""
Navigation helpers for multi-section surveys.
"""
from typing import Optional, Dict, Any
from .models import Section, Survey
from .branch_logic import BranchEvaluator


class SectionNavigator:
    """
    Handles section navigation logic including branch rules.
    """
    
    def __init__(self, survey: Survey):
        self.survey = survey
    
    def get_first_section(self) -> Optional[Section]:
        """Get first section of survey."""
        return BranchEvaluator.get_first_section(self.survey)
    
    def get_next_section(self, current_section: Section, answers: Dict[int, Any]) -> Optional[Section]:
        """
        Get next section based on branch rules and answers.
        
        Args:
            current_section: Current section
            answers: Dict of question_id -> answer_value
            
        Returns:
            Next section or None (end survey)
        """
        # Evaluate branch rules first
        evaluator = BranchEvaluator(current_section)
        next_section = evaluator.evaluate(answers)
        
        if next_section is not None:
            # Rule matched: could be Section object or None (end survey)
            return next_section
        
        # No rule matched, use sequential navigation
        return BranchEvaluator.get_next_section_sequential(current_section)
    
    def get_previous_section(self, current_section: Section) -> Optional[Section]:
        """
        Get previous section (always sequential, ignore branch rules).
        
        Args:
            current_section: Current section
            
        Returns:
            Previous section or None if first
        """
        return BranchEvaluator.get_previous_section(current_section)
    
    def is_first_section(self, section: Section) -> bool:
        """Check if section is first in survey."""
        first = self.get_first_section()
        return first and first.id == section.id
    
    def is_last_section(self, section: Section, answers: Dict[int, Any]) -> bool:
        """
        Check if section is last (considering branch rules).
        
        Args:
            section: Section to check
            answers: Current answers
            
        Returns:
            True if no next section exists
        """
        next_section = self.get_next_section(section, answers)
        return next_section is None
    
    def get_section_progress(self, current_section: Section) -> tuple:
        """
        Get progress as (current_number, total_sections).
        
        Note: This is simplified and doesn't account for skipped sections.
        
        Args:
            current_section: Current section
            
        Returns:
            Tuple of (current_position, total_count)
        """
        all_sections = Section.objects.filter(survey=self.survey).order_by('ordering')
        total = all_sections.count()
        
        current_pos = 1
        for i, section in enumerate(all_sections, 1):
            if section.id == current_section.id:
                current_pos = i
                break
        
        return (current_pos, total)
