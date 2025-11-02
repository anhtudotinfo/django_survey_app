"""
Management command to setup all initial data for deployment.

This command runs all setup scripts:
1. Create admin user
2. Create GPLX survey
3. Create Vehicle survey

Usage:
    python manage.py setup_initial_data
    python manage.py setup_initial_data --force  # Force recreate surveys
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Setup all initial data for deployment (admin + surveys)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recreation of surveys if they already exist',
        )

    def handle(self, *args, **options):
        force = options['force']
        
        self.stdout.write(
            self.style.SUCCESS(
                '=' * 70
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                '  THIẾT LẬP DỮ LIỆU BAN ĐẦU - CÔNG AN PHƯỜNG AN KHÊ'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                '=' * 70
            )
        )
        self.stdout.write('')
        
        # Step 1: Create admin user
        self.stdout.write(
            self.style.WARNING(
                '📌 Bước 1/3: Tạo tài khoản admin...'
            )
        )
        call_command('create_admin')
        self.stdout.write('')
        
        # Step 2: Create GPLX survey
        self.stdout.write(
            self.style.WARNING(
                '📌 Bước 2/3: Tạo mẫu khảo sát GPLX mô tô...'
            )
        )
        if force:
            call_command('create_gplx_survey', '--force')
        else:
            call_command('create_gplx_survey')
        self.stdout.write('')
        
        # Step 3: Create Vehicle survey
        self.stdout.write(
            self.style.WARNING(
                '📌 Bước 3/3: Tạo mẫu khảo sát Phương tiện...'
            )
        )
        if force:
            call_command('create_vehicle_survey', '--force')
        else:
            call_command('create_vehicle_survey')
        self.stdout.write('')
        
        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                '=' * 70
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                '✅ HOÀN THÀNH THIẾT LẬP DỮ LIỆU BAN ĐẦU'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                '=' * 70
            )
        )
        self.stdout.write('')
        self.stdout.write('📊 Tóm tắt:')
        self.stdout.write('   ✓ Tài khoản admin: admin / Vbpo@12345')
        self.stdout.write('   ✓ Mẫu GPLX: /surveys/khai-bao-gplx-mo-to/')
        self.stdout.write('   ✓ Mẫu Phương tiện: /surveys/khai-bao-phuong-tien/')
        self.stdout.write('')
        self.stdout.write(
            self.style.WARNING(
                '⚠️  Lưu ý quan trọng:'
            )
        )
        self.stdout.write('   1. Đổi mật khẩu admin sau lần đăng nhập đầu tiên')
        self.stdout.write('   2. Cấu hình branching logic trong admin nếu cần')
        self.stdout.write('   3. Xem QR code tại trang chủ để chia sẻ khảo sát')
        self.stdout.write('')
