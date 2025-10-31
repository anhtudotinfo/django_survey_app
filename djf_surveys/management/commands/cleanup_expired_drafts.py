"""
Management command to cleanup expired draft responses.
Run with: python manage.py cleanup_expired_drafts
"""
from django.core.management.base import BaseCommand
from djf_surveys.draft_service import DraftService


class Command(BaseCommand):
    help = 'Delete expired draft survey responses'

    def handle(self, *args, **options):
        self.stdout.write('Cleaning up expired drafts...')
        deleted_count = DraftService.cleanup_expired_drafts()
        
        if deleted_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully deleted {deleted_count} expired draft(s)')
            )
        else:
            self.stdout.write('No expired drafts found')
