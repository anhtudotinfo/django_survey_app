"""
Draft response service for saving and loading survey progress.
"""
from typing import Optional, Dict, Any
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.conf import settings
from .models import DraftResponse, Survey, Section

User = get_user_model()


class DraftService:
    """
    Service for managing draft survey responses.
    """
    
    @staticmethod
    def save_draft(
        survey: Survey,
        data: Dict[int, Any],
        user: Optional[User] = None,
        session_key: Optional[str] = None,
        current_section: Optional[Section] = None
    ) -> DraftResponse:
        """
        Save or update draft response.
        
        Args:
            survey: Survey object
            data: Dict of question_id -> answer_value
            user: Authenticated user (optional)
            session_key: Session key for anonymous users (optional)
            current_section: Current section user is on
            
        Returns:
            DraftResponse object
        """
        if not user and not session_key:
            raise ValueError("Either user or session_key must be provided")
        
        # Calculate expiration
        expiry_days = getattr(settings, 'SURVEY_DRAFT_EXPIRY_DAYS', 30)
        expires_at = timezone.now() + timedelta(days=expiry_days)
        
        # Find existing draft
        if user:
            draft = DraftResponse.objects.filter(survey=survey, user=user).first()
        else:
            draft = DraftResponse.objects.filter(survey=survey, session_key=session_key).first()
        
        if draft:
            # Update existing draft
            # Merge new data with existing data
            existing_data = draft.data or {}
            existing_data.update(data)
            draft.data = existing_data
            draft.current_section = current_section
            draft.expires_at = expires_at  # Refresh expiration
            draft.save()
        else:
            # Create new draft
            draft = DraftResponse.objects.create(
                survey=survey,
                user=user,
                session_key=session_key,
                current_section=current_section,
                data=data,
                expires_at=expires_at
            )
        
        return draft
    
    @staticmethod
    def load_draft(
        survey: Survey,
        user: Optional[User] = None,
        session_key: Optional[str] = None
    ) -> Optional[DraftResponse]:
        """
        Load existing draft response.
        
        Args:
            survey: Survey object
            user: Authenticated user (optional)
            session_key: Session key for anonymous users (optional)
            
        Returns:
            DraftResponse object or None
        """
        if not user and not session_key:
            return None
        
        # Find draft
        if user:
            draft = DraftResponse.objects.filter(
                survey=survey,
                user=user,
                expires_at__gt=timezone.now()
            ).first()
        else:
            draft = DraftResponse.objects.filter(
                survey=survey,
                session_key=session_key,
                expires_at__gt=timezone.now()
            ).first()
        
        return draft
    
    @staticmethod
    def delete_draft(
        survey: Survey,
        user: Optional[User] = None,
        session_key: Optional[str] = None
    ) -> bool:
        """
        Delete draft response.
        
        Args:
            survey: Survey object
            user: Authenticated user (optional)
            session_key: Session key for anonymous users (optional)
            
        Returns:
            True if deleted, False if not found
        """
        if user:
            deleted, _ = DraftResponse.objects.filter(survey=survey, user=user).delete()
        elif session_key:
            deleted, _ = DraftResponse.objects.filter(survey=survey, session_key=session_key).delete()
        else:
            return False
        
        return deleted > 0
    
    @staticmethod
    def convert_to_final(draft: DraftResponse) -> None:
        """
        Convert draft to final response and delete draft.
        Called after survey submission.
        
        Args:
            draft: DraftResponse object to convert
        """
        # Final response already saved by form, just delete draft
        draft.delete()
    
    @staticmethod
    def cleanup_expired_drafts() -> int:
        """
        Delete all expired drafts.
        Should be called by scheduled task (cron job).
        
        Returns:
            Number of drafts deleted
        """
        deleted, _ = DraftResponse.objects.filter(
            expires_at__lte=timezone.now()
        ).delete()
        return deleted
    
    @staticmethod
    def get_draft_data_for_form(draft: DraftResponse) -> Dict[str, Any]:
        """
        Convert draft data to form-compatible format.
        
        Args:
            draft: DraftResponse object
            
        Returns:
            Dict with field names as keys
        """
        from datetime import datetime
        
        form_data = {}
        if draft.data:
            for question_id, value in draft.data.items():
                field_name = f'field_survey_{question_id}'
                # Convert ISO date strings back to date objects if needed
                if isinstance(value, str) and len(value) == 10 and value.count('-') == 2:
                    try:
                        # Try to parse as date (YYYY-MM-DD format)
                        from datetime import date
                        value = date.fromisoformat(value)
                    except (ValueError, AttributeError):
                        pass  # Keep as string if parsing fails
                form_data[field_name] = value
        
        return form_data
    
    @staticmethod
    def extract_answers_from_form(form_data: Dict[str, Any]) -> Dict[int, Any]:
        """
        Extract question answers from form data.
        
        Args:
            form_data: Form cleaned_data dict
            
        Returns:
            Dict mapping question_id to answer value
        """
        from datetime import date, datetime
        
        answers = {}
        for field_name, value in form_data.items():
            if field_name.startswith('field_survey_'):
                # Extract question ID from field name
                try:
                    question_id = int(field_name.replace('field_survey_', ''))
                    # Handle file fields - don't store in draft (need special handling)
                    if not hasattr(value, 'read'):  # Not a file object
                        # Convert date/datetime to string for JSON serialization
                        if isinstance(value, (date, datetime)):
                            value = value.isoformat()
                        answers[question_id] = value
                except (ValueError, AttributeError):
                    continue
        
        return answers
