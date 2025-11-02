"""
Management command to create Vehicle Information survey template.

Usage:
    python manage.py create_vehicle_survey
    python manage.py create_vehicle_survey --force  # Recreate if exists
"""

from django.core.management.base import BaseCommand
from djf_surveys.models import Survey, Section, Question, TYPE_FIELD


class Command(BaseCommand):
    help = 'Create vehicle information declaration survey template'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recreation if survey already exists',
        )

    def handle(self, *args, **options):
        force = options['force']
        survey_slug = 'khai-bao-phuong-tien'
        
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
                name='KHAI BÁO THÔNG TIN PHƯƠNG TIỆN',
                slug=survey_slug,
                description='Kê khai thông tin phương tiện (ô tô, mô tô, xe máy điện…) để phục vụ việc làm sạch dữ liệu đăng ký xe theo Kế hoạch của CATP Đà Nẵng.',
                can_anonymous_user=True,
                duplicate_entry=False,
                editable=True,
                deletable=False,
                private_response=True,
                file_organization='response',
                success_page_content='<h2>Cảm ơn bạn đã khai báo thông tin phương tiện!</h2><p>Thông tin của bạn đã được ghi nhận. Công an phường An Khê sẽ xử lý và cập nhật dữ liệu.</p>'
            )
            
            self.stdout.write(f'Created survey: {survey.name}')
            
            # Section 1: Hướng dẫn chung
            section1 = Section.objects.create(
                survey=survey,
                name='PHẦN 1 - HƯỚNG DẪN CHUNG',
                description='''<div class="bg-green-50 p-4 rounded-lg mb-4">
<h3 class="font-bold text-lg mb-2">📋 HƯỚNG DẪN</h3>
<p class="mb-2">Kính đề nghị công dân đang cư trú tại phường An Khê kê khai thông tin phương tiện (ô tô, mô tô, xe máy điện…) để phục vụ việc làm sạch dữ liệu đăng ký xe theo Kế hoạch của CATP Đà Nẵng.</p>
<p class="mb-2">⏱ <strong>Thời gian:</strong> từ 01/11 – 30/11/2025</p>
<p class="mb-2">📸 <strong>Chuẩn bị:</strong> CCCD và cà-vẹt xe để chụp ảnh.</p>
<p>📝 Mỗi người có thể kê khai tối đa 3 phương tiện trong cùng biểu mẫu này.</p>
</div>''',
                ordering=0
            )
            
            # Section 2: Thông tin chủ phương tiện
            section2 = Section.objects.create(
                survey=survey,
                name='PHẦN 2 - THÔNG TIN CHỦ PHƯƠNG TIỆN',
                description='Vui lòng điền đầy đủ thông tin chủ xe để đối chiếu với CSDL C06.',
                ordering=1
            )
            
            order = 0
            # Questions in Section 2
            Question.objects.create(
                survey=survey, section=section2, ordering=order, type_field=TYPE_FIELD.text,
                label='Họ và tên chủ phương tiện', required=True
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
                label='Địa chỉ tạm trú (nếu khác thường trú)', required=False,
                help_text='Giúp đối chiếu dữ liệu thực tế'
            ); order += 1
            
            Question.objects.create(
                survey=survey, section=section2, ordering=order, type_field=TYPE_FIELD.text,
                label='Tổ dân phố', required=True,
                help_text='Nhập số tổ (1-262)'
            ); order += 1
            
            Question.objects.create(
                survey=survey, section=section2, ordering=order, type_field=TYPE_FIELD.radio,
                label='Tình trạng cư trú của chủ xe', required=True,
                choices='Còn cư trú,Đã chuyển đi,Đã mất,Không rõ'
            ); order += 1
            
            Question.objects.create(
                survey=survey, section=section2, ordering=order, type_field=TYPE_FIELD.text_area,
                label='Địa chỉ mới (nếu đã chuyển đi)', required=False,
                help_text='Chỉ điền nếu chọn "Đã chuyển đi" ở câu trước'
            ); order += 1
            
            # Section 3: Chọn số lượng xe
            section3 = Section.objects.create(
                survey=survey,
                name='PHẦN 3 - CHỌN SỐ LƯỢNG XE',
                description='Vui lòng chọn số lượng phương tiện bạn muốn kê khai.',
                ordering=2
            )
            
            # Create branching question
            branch_question = Question.objects.create(
                survey=survey,
                section=section3,
                ordering=100,
                type_field=TYPE_FIELD.radio,
                label='Anh/chị có bao nhiêu phương tiện đứng tên?',
                choices='1 xe,2 xe,3 xe',
                required=True,
                enable_branching=True
            )
            
            # Section 4: Xe 1
            section4 = Section.objects.create(
                survey=survey,
                name='PHẦN 4 - PHƯƠNG TIỆN THỨ NHẤT',
                description='Thông tin chi tiết về phương tiện thứ nhất',
                ordering=3
            )
            
            order = 200
            Question.objects.create(
                survey=survey, section=section4, ordering=order, type_field=TYPE_FIELD.text,
                label='Biển số xe 1', required=True,
                help_text='VD: 43A-12345'
            ); order += 1
            
            Question.objects.create(
                survey=survey, section=section4, ordering=order, type_field=TYPE_FIELD.select,
                label='Loại phương tiện 1', required=True,
                choices='Ô tô,Mô tô,Xe máy điện,Xe chuyên dùng'
            ); order += 1
            
            Question.objects.create(
                survey=survey, section=section4, ordering=order, type_field=TYPE_FIELD.text,
                label='Nhãn hiệu - Model xe 1', required=True,
                help_text='Ví dụ: Honda Wave, Toyota Vios...'
            ); order += 1
            
            Question.objects.create(
                survey=survey, section=section4, ordering=order, type_field=TYPE_FIELD.text,
                label='Màu sơn xe 1', required=True
            ); order += 1
            
            Question.objects.create(
                survey=survey, section=section4, ordering=order, type_field=TYPE_FIELD.number,
                label='Năm sản xuất xe 1 (nếu biết)', required=False,
                help_text='Năm sản xuất (VD: 2020)'
            ); order += 1
            
            Question.objects.create(
                survey=survey, section=section4, ordering=order, type_field=TYPE_FIELD.radio,
                label='Tình trạng phương tiện 1', required=True,
                choices='Đang sử dụng,Đã bán,Hết niên hạn,Không còn trên địa bàn,Khác'
            ); order += 1
            
            Question.objects.create(
                survey=survey, section=section4, ordering=order, type_field=TYPE_FIELD.text,
                label='Nếu đã bán/chuyển nhượng xe 1, nhập người mua (nếu biết)', required=False
            ); order += 1
            
            Question.objects.create(
                survey=survey, section=section4, ordering=order, type_field=TYPE_FIELD.file,
                label='Ảnh cà-vẹt xe 1 (mặt trước)', required=True,
                help_text='Định dạng: .jpg/.png, Kích thước tối đa: 5MB'
            ); order += 1
            
            Question.objects.create(
                survey=survey, section=section4, ordering=order, type_field=TYPE_FIELD.file,
                label='Ảnh biển số xe 1 (tùy chọn)', required=False,
                help_text='Định dạng: .jpg/.png, Kích thước tối đa: 5MB'
            ); order += 1
            
            # Section 5: Xe 2
            section5 = Section.objects.create(
                survey=survey,
                name='PHẦN 5 - PHƯƠNG TIỆN THỨ HAI',
                description='Thông tin chi tiết về phương tiện thứ hai (nếu có)',
                ordering=4
            )
            
            order = 300
            Question.objects.create(
                survey=survey, section=section5, ordering=order, type_field=TYPE_FIELD.text,
                label='Biển số xe 2', required=True
            ); order += 1
            
            Question.objects.create(
                survey=survey, section=section5, ordering=order, type_field=TYPE_FIELD.select,
                label='Loại phương tiện 2', required=True,
                choices='Ô tô,Mô tô,Xe máy điện,Xe chuyên dùng'
            ); order += 1
            
            Question.objects.create(
                survey=survey, section=section5, ordering=order, type_field=TYPE_FIELD.text,
                label='Nhãn hiệu - Model xe 2', required=True
            ); order += 1
            
            Question.objects.create(
                survey=survey, section=section5, ordering=order, type_field=TYPE_FIELD.text,
                label='Màu sơn xe 2', required=True
            ); order += 1
            
            Question.objects.create(
                survey=survey, section=section5, ordering=order, type_field=TYPE_FIELD.number,
                label='Năm sản xuất xe 2 (nếu biết)', required=False
            ); order += 1
            
            Question.objects.create(
                survey=survey, section=section5, ordering=order, type_field=TYPE_FIELD.radio,
                label='Tình trạng phương tiện 2', required=True,
                choices='Đang sử dụng,Đã bán,Hết niên hạn,Không còn trên địa bàn,Khác'
            ); order += 1
            
            Question.objects.create(
                survey=survey, section=section5, ordering=order, type_field=TYPE_FIELD.text,
                label='Nếu đã bán/chuyển nhượng xe 2, nhập người mua (nếu biết)', required=False
            ); order += 1
            
            Question.objects.create(
                survey=survey, section=section5, ordering=order, type_field=TYPE_FIELD.file,
                label='Ảnh cà-vẹt xe 2 (mặt trước)', required=True
            ); order += 1
            
            Question.objects.create(
                survey=survey, section=section5, ordering=order, type_field=TYPE_FIELD.file,
                label='Ảnh biển số xe 2 (tùy chọn)', required=False
            ); order += 1
            
            # Section 6: Xe 3
            section6 = Section.objects.create(
                survey=survey,
                name='PHẦN 6 - PHƯƠNG TIỆN THỨ BA',
                description='Thông tin chi tiết về phương tiện thứ ba (nếu có)',
                ordering=5
            )
            
            order = 400
            Question.objects.create(
                survey=survey, section=section6, ordering=order, type_field=TYPE_FIELD.text,
                label='Biển số xe 3', required=True
            ); order += 1
            
            Question.objects.create(
                survey=survey, section=section6, ordering=order, type_field=TYPE_FIELD.select,
                label='Loại phương tiện 3', required=True,
                choices='Ô tô,Mô tô,Xe máy điện,Xe chuyên dùng'
            ); order += 1
            
            Question.objects.create(
                survey=survey, section=section6, ordering=order, type_field=TYPE_FIELD.text,
                label='Nhãn hiệu - Model xe 3', required=True
            ); order += 1
            
            Question.objects.create(
                survey=survey, section=section6, ordering=order, type_field=TYPE_FIELD.text,
                label='Màu sơn xe 3', required=True
            ); order += 1
            
            Question.objects.create(
                survey=survey, section=section6, ordering=order, type_field=TYPE_FIELD.number,
                label='Năm sản xuất xe 3 (nếu biết)', required=False
            ); order += 1
            
            Question.objects.create(
                survey=survey, section=section6, ordering=order, type_field=TYPE_FIELD.radio,
                label='Tình trạng phương tiện 3', required=True,
                choices='Đang sử dụng,Đã bán,Hết niên hạn,Không còn trên địa bàn,Khác'
            ); order += 1
            
            Question.objects.create(
                survey=survey, section=section6, ordering=order, type_field=TYPE_FIELD.text,
                label='Nếu đã bán/chuyển nhượng xe 3, nhập người mua (nếu biết)', required=False
            ); order += 1
            
            Question.objects.create(
                survey=survey, section=section6, ordering=order, type_field=TYPE_FIELD.file,
                label='Ảnh cà-vẹt xe 3 (mặt trước)', required=True
            ); order += 1
            
            Question.objects.create(
                survey=survey, section=section6, ordering=order, type_field=TYPE_FIELD.file,
                label='Ảnh biển số xe 3 (tùy chọn)', required=False
            ); order += 1
            
            # Section 7: Cam kết
            section7 = Section.objects.create(
                survey=survey,
                name='PHẦN 7 - CAM KẾT VÀ GỬI',
                description='',
                ordering=6
            )
            
            Question.objects.create(
                survey=survey,
                section=section7,
                ordering=500,
                type_field=TYPE_FIELD.radio,
                label='Tôi cam kết thông tin khai báo là đúng sự thật và đồng ý để Công an phường An Khê sử dụng dữ liệu này phục vụ công tác quản lý, làm sạch, cập nhật cơ sở dữ liệu phương tiện.',
                choices='Tôi đồng ý và cam kết',
                required=True
            )
            
            # Configure branching logic
            branch_question.branch_config = {
                '1_xe': section4.id,
                '2_xe': section4.id,
                '3_xe': section4.id
            }
            branch_question.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Successfully created Vehicle survey'
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
