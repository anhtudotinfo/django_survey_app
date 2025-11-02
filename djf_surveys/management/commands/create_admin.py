"""
Management command to create admin user for deployment.

Usage:
    python manage.py create_admin
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Create admin user with fixed password for deployment'

    def handle(self, *args, **options):
        username = 'admin'
        email = 'admin@ankhe.police.vn'
        password = 'Vbpo@12345'
        
        # Check if admin user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(
                    f'⚠️  Admin user "{username}" already exists - skipping creation'
                )
            )
            return
        
        # Create superuser
        try:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Successfully created admin user'
                )
            )
            self.stdout.write(f'   Username: {username}')
            self.stdout.write(f'   Email: {email}')
            self.stdout.write(f'   Password: {password}')
            self.stdout.write('')
            self.stdout.write(
                self.style.WARNING(
                    '⚠️  IMPORTANT: Change the password after first login!'
                )
            )
            self.stdout.write(f'   Admin URL: /admin/')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'❌ Error creating admin user: {str(e)}'
                )
            )
