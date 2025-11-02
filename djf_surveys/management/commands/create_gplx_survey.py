"""
Management command to create GPLX (Motorcycle License) survey template.

Usage:
    python manage.py create_gplx_survey
    python manage.py create_gplx_survey --force  # Recreate if exists
"""

from django.core.management.base import BaseCommand
from djf_surveys.models import Survey, Section, Question, TYPE_FIELD


class Command(BaseCommand):
    help = 'Create GPLX motorcycle license declaration survey template'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recreation if survey already exists',
        )

    def handle(self, *args, **options):
        force = options['force']
        survey_slug = 'khai-bao-gplx-mo-to'
        
        # Check if survey exists
        existing = Survey.objects.filter(slug=survey_slug).first()
        if existing and not force:
            self.stdout.write(
                self.style.WARNING(
                    f'⚠️  Survey "{existing.name}" already exists (ID: {existing.id})'
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    'Use --force to recreate'
                )
            )
            return
        
        if existing and force:
            self.stdout.write(
                self.style.WARNING(
                    f'Deleting existing survey: {existing.name}'
                )
            )
            existing.delete()
        
        try:
            # Create survey
            survey = Survey.objects.create(
                name='KHAI BÁO GIẤY PHÉP LÁI XE MÔ TÔ',
                slug=survey_slug,
                description='Kê khai thông tin Giấy phép lái xe mô tô (loại giấy bìa cũ) để phục vụ làm sạch, bổ sung và đồng bộ dữ liệu GPLX.',
                can_anonymous_user=True,
                duplicate_entry=False,
                editable=True,
                deletable=False,
                private_response=True,
                file_organization='response',
                success_page_content='<h2>Cảm ơn bạn đã khai báo thông tin GPLX!</h2><p>Thông tin của bạn đã được ghi nhận. Công an phường An Khê sẽ xử lý và cập nhật dữ liệu.</p>'
            )
            
            self.stdout.write(f'Created survey: {survey.name}')
            
            # Section 1: Hướng dẫn mở đầu
            section1 = Section.objects.create(
                survey=survey,
                name='PHẦN 1 - HƯỚNG DẪN MỞ ĐẦU',
                description='''<div class="bg-blue-50 p-4 rounded-lg mb-4">
<h3 class="font-bold text-lg mb-2">📋 HƯỚNG DẪN</h3>
<p class="mb-2">Kính đề nghị công dân đang cư trú tại phường An Khê kê khai thông tin Giấy phép lái xe mô tô (loại giấy bìa cũ) để phục vụ làm sạch, bổ sung và đồng bộ dữ liệu GPLX với CSDL dân cư và đăng ký phương tiện.</p>
<p class="mb-2">⏱ <strong>Thời gian:</strong> từ 01/11 đến 15/12/2025</p>
<p class="mb-2">⚠️ <strong>Lưu ý:</strong> Nếu đã đổi sang thẻ PET hoặc GPLX điện tử, không cần kê khai lại.</p>
<p>📝 Người có nhiều hơn một GPLX mô tô (A1, A2, A3...) có thể kê khai tối đa 3 GPLX trong cùng biểu mẫu này.</p>
</div>''',
                ordering=0
            )
            
            # Section 2: Thông tin người khai
            section2 = Section.objects.create(
                survey=survey,
                name='PHẦN 2 - THÔNG TIN NGƯỜI KHAI',
                description='Vui lòng điền đầy đủ thông tin cá nhân để đối chiếu với CSDL C06 (dân cư).',
                ordering=1
            )
            
            order = 0
            # Questions in Section 2
            Question.objects.create(
                survey=survey, section=section2, ordering=order, type_field=TYPE_FIELD.text,
                label='Họ và tên', required=True
            ); order += 1
            
            Question.objects.create(
                survey=survey, section=section2, ordering=order, type_field=TYPE_FIELD.text,
                label='Số CCCD/CMND', required=True,
                regex_pattern=r'^[0-9]{9}$|^[0-9]{12}$',
                validation_message='Vui lòng nhập số CCCD 9 hoặc 12 số'
            ); order += 1
            
            Question.objects.create(
                survey=survey, section=section2, ordering=order, type_field=TYPE_FIELD.date,
                label='Ngày tháng năm sinh', required=True
            ); order += 1
            
            Question.objects.create(
                survey=survey, section=section2, ordering=order, type_field=TYPE_FIELD.radio,
                label='Giới tính', required=True, choices='Nam,Nữ'
            ); order += 1
            
            Question.objects.create(
                survey=survey, section=section2, ordering=order, type_field=TYPE_FIELD.text,
                label='Số điện thoại liên hệ', required=True,
                regex_pattern=r'^[0-9]{10}$',
                validation_message='Vui lòng nhập số điện thoại 10 số'
            ); order += 1
            
            Question.objects.create(
                survey=survey, section=section2, ordering=order, type_field=TYPE_FIELD.text_area,
                label='Địa chỉ thường trú', required=True,
                help_text='Ghi theo CCCD'
            ); order += 1
            
            Question.objects.create(
                survey=survey, section=section2, ordering=order, type_field=TYPE_FIELD.text_area,
                label='Địa chỉ tạm trú (nếu có)', required=False
            ); order += 1
            
            Question.objects.create(
                survey=survey, section=section2, ordering=order, type_field=TYPE_FIELD.text,
                label='Tổ dân phố', required=True,
                help_text='Nhập số tổ (1-262)'
            ); order += 1
            
            # Section 3: Chọn số lượng GPLX
            section3 = Section.objects.create(
                survey=survey,
                name='PHẦN 3 - CHỌN SỐ LƯỢNG GPLX CẦN KHAI',
                description='Vui lòng chọn số lượng giấy phép lái xe mô tô bạn muốn kê khai.',
                ordering=2
            )
            
            # Create branching question
            branch_question = Question.objects.create(
                survey=survey,
                section=section3,
                ordering=100,
                type_field=TYPE_FIELD.radio,
                label='Anh/chị có bao nhiêu giấy phép lái xe mô tô đang giữ hoặc đã cấp trước đây?',
                choices='1 GPLX,2 GPLX,3 GPLX',
                required=True,
                enable_branching=True
            )
            
            # Section 4: GPLX 1
            section4 = Section.objects.create(
                survey=survey,
                name='PHẦN 4 - GIẤY PHÉP LÁI XE THỨ NHẤT',
                description='Thông tin chi tiết về GPLX thứ nhất',
                ordering=3
            )
            
            order = 200
            Question.objects.create(
                survey=survey, section=section4, ordering=order, type_field=TYPE_FIELD.text,
                label='Số GPLX 1', required=True
            ); order += 1
            
            Question.objects.create(
                survey=survey, section=section4, ordering=order, type_field=TYPE_FIELD.select,
                label='Hạng GPLX 1', required=True, choices='A1,A2,A3,A4'
            ); order += 1
            
            Question.objects.create(
                survey=survey, section=section4, ordering=order, type_field=TYPE_FIELD.date,
                label='Ngày cấp GPLX 1', required=True
            ); order += 1
            
            Question.objects.create(
                survey=survey, section=section4, ordering=order, type_field=TYPE_FIELD.text,
                label='Nơi cấp GPLX 1', required=True,
                help_text='VD: Sở GTVT Đà Nẵng'
            ); order += 1
            
            Question.objects.create(
                survey=survey, section=section4, ordering=order, type_field=TYPE_FIELD.radio,
                label='Tình trạng GPLX 1', required=True,
                choices='Còn sử dụng,Đã đổi sang PET,Mất,Hết hạn'
            ); order += 1
            
            Question.objects.create(
                survey=survey, section=section4, ordering=order, type_field=TYPE_FIELD.file,
                label='Ảnh mặt trước GPLX 1', required=True,
                help_text='Định dạng: .jpg/.png, Kích thước tối đa: 5MB'
            ); order += 1
            
            Question.objects.create(
                survey=survey, section=section4, ordering=order, type_field=TYPE_FIELD.file,
                label='Ảnh mặt sau GPLX 1', required=False,
                help_text='Định dạng: .jpg/.png, Kích thước tối đa: 5MB'
            ); order += 1
            
            # Section 5: GPLX 2
            section5 = Section.objects.create(
                survey=survey,
                name='PHẦN 5 - GIẤY PHÉP LÁI XE THỨ HAI',
                description='Thông tin chi tiết về GPLX thứ hai (nếu có)',
                ordering=4
            )
            
            order = 300
            Question.objects.create(
                survey=survey, section=section5, ordering=order, type_field=TYPE_FIELD.text,
                label='Số GPLX 2', required=True
            ); order += 1
            
            Question.objects.create(
                survey=survey, section=section5, ordering=order, type_field=TYPE_FIELD.select,
                label='Hạng GPLX 2', required=True, choices='A1,A2,A3,A4'
            ); order += 1
            
            Question.objects.create(
                survey=survey, section=section5, ordering=order, type_field=TYPE_FIELD.date,
                label='Ngày cấp GPLX 2', required=True
            ); order += 1
            
            Question.objects.create(
                survey=survey, section=section5, ordering=order, type_field=TYPE_FIELD.text,
                label='Nơi cấp GPLX 2', required=True
            ); order += 1
            
            Question.objects.create(
                survey=survey, section=section5, ordering=order, type_field=TYPE_FIELD.radio,
                label='Tình trạng GPLX 2', required=True,
                choices='Còn sử dụng,Đã đổi sang PET,Mất,Hết hạn'
            ); order += 1
            
            Question.objects.create(
                survey=survey, section=section5, ordering=order, type_field=TYPE_FIELD.file,
                label='Ảnh mặt trước GPLX 2', required=True
            ); order += 1
            
            Question.objects.create(
                survey=survey, section=section5, ordering=order, type_field=TYPE_FIELD.file,
                label='Ảnh mặt sau GPLX 2', required=False
            ); order += 1
            
            # Section 6: GPLX 3
            section6 = Section.objects.create(
                survey=survey,
                name='PHẦN 6 - GIẤY PHÉP LÁI XE THỨ BA',
                description='Thông tin chi tiết về GPLX thứ ba (nếu có)',
                ordering=5
            )
            
            order = 400
            Question.objects.create(
                survey=survey, section=section6, ordering=order, type_field=TYPE_FIELD.text,
                label='Số GPLX 3', required=True
            ); order += 1
            
            Question.objects.create(
                survey=survey, section=section6, ordering=order, type_field=TYPE_FIELD.select,
                label='Hạng GPLX 3', required=True, choices='A1,A2,A3,A4'
            ); order += 1
            
            Question.objects.create(
                survey=survey, section=section6, ordering=order, type_field=TYPE_FIELD.date,
                label='Ngày cấp GPLX 3', required=True
            ); order += 1
            
            Question.objects.create(
                survey=survey, section=section6, ordering=order, type_field=TYPE_FIELD.text,
                label='Nơi cấp GPLX 3', required=True
            ); order += 1
            
            Question.objects.create(
                survey=survey, section=section6, ordering=order, type_field=TYPE_FIELD.radio,
                label='Tình trạng GPLX 3', required=True,
                choices='Còn sử dụng,Đã đổi sang PET,Mất,Hết hạn'
            ); order += 1
            
            Question.objects.create(
                survey=survey, section=section6, ordering=order, type_field=TYPE_FIELD.file,
                label='Ảnh mặt trước GPLX 3', required=True
            ); order += 1
            
            Question.objects.create(
                survey=survey, section=section6, ordering=order, type_field=TYPE_FIELD.file,
                label='Ảnh mặt sau GPLX 3', required=False
            ); order += 1
            
            # Section 7: Cam kết
            section7 = Section.objects.create(
                survey=survey,
                name='PHẦN 7 - CAM KẾT',
                description='',
                ordering=6
            )
            
            Question.objects.create(
                survey=survey,
                section=section7,
                ordering=500,
                type_field=TYPE_FIELD.radio,
                label='Tôi cam kết thông tin kê khai là đúng sự thật và đồng ý để Công an phường An Khê sử dụng dữ liệu này phục vụ công tác làm sạch, đồng bộ và quản lý giấy phép lái xe.',
                choices='Tôi đồng ý và cam kết',
                required=True
            )
            
            # Configure branching logic
            branch_question.branch_config = {
                '1_gplx': section4.id,
                '2_gplx': section4.id,
                '3_gplx': section4.id
            }
            branch_question.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Successfully created GPLX survey'
                )
            )
            self.stdout.write(f'   Survey ID: {survey.id}')
            self.stdout.write(f'   Survey slug: {survey.slug}')
            self.stdout.write(f'   URL: /surveys/{survey.slug}/')
            self.stdout.write(f'   Sections created: 7')
            self.stdout.write(f'   Total questions: {survey.questions.count()}')
            self.stdout.write('')
            self.stdout.write(
                self.style.WARNING(
                    '⚠️  Note: Branching logic requires manual configuration in admin'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'❌ Error creating survey: {str(e)}'
                )
            )
            import traceback
            traceback.print_exc()
