"""
Management command to initialize default site configuration.

Usage:
    python manage.py init_siteconfig
    python manage.py init_siteconfig --force  # Force recreate
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import gettext as _
from djf_surveys.models import SiteConfig


class Command(BaseCommand):
    help = 'Initialize default site configuration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force creation of new config (deactivates existing)',
        )
        
        parser.add_argument(
            '--site-name',
            type=str,
            default='Survey System',
            help='Site name (default: Survey System)',
        )

    def handle(self, *args, **options):
        force = options['force']
        site_name = options['site_name']
        
        # Check if config exists
        existing = SiteConfig.objects.filter(is_active=True).first()
        
        if existing and not force:
            self.stdout.write(
                self.style.WARNING(
                    f'Active configuration already exists: {existing.site_name} (v{existing.version})'
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    'Use --force to create a new configuration'
                )
            )
            return
        
        if force and existing:
            existing.is_active = False
            existing.save()
            self.stdout.write(
                self.style.WARNING(
                    f'Deactivated existing config: {existing.site_name} (v{existing.version})'
                )
            )
        
        # Create default configuration
        config = SiteConfig.objects.create(
            site_name=site_name,
            site_tagline="Hệ thống khảo sát trực tuyến",
            is_active=True,
            
            # Colors
            primary_color="#6366f1",
            secondary_color="#8b5cf6",
            accent_color="#ec4899",
            
            # Homepage
            homepage_title="Chào mừng đến với Hệ thống Khảo sát",
            homepage_subtitle="Nền tảng khảo sát trực tuyến hiện đại và dễ sử dụng. "
                             "Tạo, quản lý và phân tích khảo sát một cách chuyên nghiệp.",
            
            # Footer
            footer_text="© 2025 Survey System. All rights reserved.",
            footer_address="123 Main Street, City, Country",
            footer_phone="+84 123 456 789",
            footer_email="support@surveyystem.com",
            
            # Static pages
            about_page_content="""
            <h2>Giới thiệu về hệ thống</h2>
            <p>Hệ thống khảo sát trực tuyến của chúng tôi giúp bạn:</p>
            <ul>
                <li>Tạo khảo sát dễ dàng với nhiều loại câu hỏi</li>
                <li>Thu thập phản hồi từ người dân</li>
                <li>Phân tích kết quả chi tiết</li>
                <li>Quản lý dữ liệu an toàn</li>
            </ul>
            """,
            
            contact_page_content="""
            <h2>Liên hệ với chúng tôi</h2>
            <p>Nếu bạn cần hỗ trợ, vui lòng liên hệ:</p>
            <ul>
                <li>Email: support@surveysystem.com</li>
                <li>Điện thoại: +84 123 456 789</li>
                <li>Địa chỉ: 123 Main Street, City</li>
            </ul>
            """,
            
            terms_page_content="""
            <h2>Điều khoản sử dụng</h2>
            <p>Vui lòng đọc kỹ các điều khoản sau trước khi sử dụng hệ thống...</p>
            """,
            
            privacy_page_content="""
            <h2>Chính sách bảo mật</h2>
            <p>Chúng tôi cam kết bảo vệ thông tin cá nhân của bạn...</p>
            """,
            
            # Features
            enable_user_registration=True,
            enable_anonymous_surveys=True,
            show_survey_stats=True,
            
            # SEO
            meta_description="Hệ thống khảo sát trực tuyến hiện đại - Tạo và quản lý khảo sát dễ dàng",
            meta_keywords="khảo sát, survey, trực tuyến, online, feedback, phản hồi",
            
            # Notes
            notes="Default configuration created by init_siteconfig command",
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Successfully created site configuration: {config.site_name} (v{config.version})'
            )
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Configuration ID: {config.id}'
            )
        )
        
        self.stdout.write(
            self.style.WARNING(
                '\n💡 Next steps:'
            )
        )
        self.stdout.write('   1. Go to admin: /admin/djf_surveys/siteconfig/')
        self.stdout.write('   2. Upload logo and favicon')
        self.stdout.write('   3. Customize colors and content')
        self.stdout.write('   4. Add social media links')
