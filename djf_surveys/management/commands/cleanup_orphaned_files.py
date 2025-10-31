"""
Management command to cleanup orphaned survey files.
Run with: python manage.py cleanup_orphaned_files
"""
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from djf_surveys.models import Answer


class Command(BaseCommand):
    help = 'Delete orphaned survey upload files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write('DRY RUN MODE - No files will be deleted')
        
        # Get survey_uploads directory
        media_root = settings.MEDIA_ROOT
        uploads_dir = os.path.join(media_root, 'survey_uploads')
        
        if not os.path.exists(uploads_dir):
            self.stdout.write('No survey_uploads directory found')
            return
        
        # Get all file paths from database
        db_files = set()
        for answer in Answer.objects.filter(file_value__isnull=False):
            if answer.file_value:
                db_files.add(answer.file_value.path)
        
        self.stdout.write(f'Found {len(db_files)} files in database')
        
        # Walk through upload directory
        orphaned_files = []
        for root, dirs, files in os.walk(uploads_dir):
            for filename in files:
                file_path = os.path.join(root, filename)
                if file_path not in db_files:
                    orphaned_files.append(file_path)
        
        self.stdout.write(f'Found {len(orphaned_files)} orphaned files')
        
        if not orphaned_files:
            self.stdout.write(self.style.SUCCESS('No orphaned files to clean up'))
            return
        
        # Delete orphaned files
        deleted_count = 0
        for file_path in orphaned_files:
            try:
                if dry_run:
                    self.stdout.write(f'Would delete: {file_path}')
                else:
                    os.remove(file_path)
                    self.stdout.write(f'Deleted: {file_path}')
                deleted_count += 1
            except Exception as e:
                self.stderr.write(f'Error deleting {file_path}: {str(e)}')
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'DRY RUN: Would delete {deleted_count} orphaned file(s)')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully deleted {deleted_count} orphaned file(s)')
            )
