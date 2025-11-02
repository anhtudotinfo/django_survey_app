#!/usr/bin/env python3
"""
Script to create GPLX (Driver's License) Survey with 3 sections and branching logic
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, '/home/tuna/Desktop/django_survey_app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moi.settings')
django.setup()

from django.contrib.auth import get_user_model
from djf_surveys.models import Survey, Question, Section, TYPE_FIELD

User = get_user_model()

def create_gplx_survey():
    """Create the GPLX survey with sections and branching"""
    
    # Get or create superuser
    try:
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            user = User.objects.create_superuser('admin', 'admin@example.com', 'admin')
            print("✓ Created admin user")
        else:
            print(f"✓ Using existing user: {user.username}")
    except Exception as e:
        print(f"✗ Error with user: {e}")
        return

    # Create Survey
    survey, created = Survey.objects.get_or_create(
        slug='gplx-declaration',
        defaults={
            'name': 'KHAI BÁO GIẤY PHÉP LÁI XE MÔ TÔ',
            'description': '''Kính đề nghị công dân đang cư trú tại phường An Khê kê khai thông tin Giấy phép lái xe mô tô (loại giấy bìa cũ) để phục vụ làm sạch, bổ sung và đồng bộ dữ liệu GPLX với CSDL dân cư và đăng ký phương tiện.

⏱ Thời gian: từ 01/11 đến 15/12/2025
⚠️ Nếu đã đổi sang thẻ PET hoặc GPLX điện tử, không cần kê khai lại.

Người có nhiều hơn một GPLX mô tô (A1, A2, A3...) có thể kê khai tối đa 3 GPLX trong cùng biểu mẫu này.''',
            'editable': True,
            'deletable': True,
            'duplicate_entry': False,
            'private_response': False,
            'can_anonymous_user': True,
        }
    )
    
    if created:
        print(f"✓ Created survey: {survey.name}")
    else:
        print(f"✓ Survey already exists: {survey.name}")
        # Clear existing sections and questions
        Section.objects.filter(survey=survey).delete()
        Question.objects.filter(survey=survey).delete()
        print("  → Cleared existing sections and questions")

    # Create Sections
    section_intro = Section.objects.create(
        survey=survey,
        name="Hướng dẫn & Thông tin người khai",
        description="Phần 1-2: Hướng dẫn và thông tin cá nhân",
        ordering=0
    )
    print(f"✓ Created section: {section_intro.name}")

    section_choose_count = Section.objects.create(
        survey=survey,
        name="Chọn số lượng GPLX",
        description="Phần 3: Anh/chị có bao nhiêu GPLX mô tô?",
        ordering=1
    )
    print(f"✓ Created section: {section_choose_count.name}")

    section_gplx1 = Section.objects.create(
        survey=survey,
        name="GPLX thứ nhất",
        description="Thông tin giấy phép lái xe thứ 1",
        ordering=2
    )
    print(f"✓ Created section: {section_gplx1.name}")

    section_gplx2 = Section.objects.create(
        survey=survey,
        name="GPLX thứ hai",
        description="Thông tin giấy phép lái xe thứ 2",
        ordering=3
    )
    print(f"✓ Created section: {section_gplx2.name}")

    section_gplx3 = Section.objects.create(
        survey=survey,
        name="GPLX thứ ba",
        description="Thông tin giấy phép lái xe thứ 3",
        ordering=4
    )
    print(f"✓ Created section: {section_gplx3.name}")

    section_commitment = Section.objects.create(
        survey=survey,
        name="Cam kết",
        description="Phần 7: Cam kết thông tin chính xác",
        ordering=5
    )
    print(f"✓ Created section: {section_commitment.name}")

    # SECTION 1: Personal Information
    print("\n📝 Creating questions for Section 1: Personal Info...")
    
    q_order = 1
    
    Question.objects.create(
        survey=survey,
        section=section_intro,
        label="Họ và tên",
        key="ho_ten",
        type_field=TYPE_FIELD.text,
        required=True,
        ordering=q_order
    )
    q_order += 1

    Question.objects.create(
        survey=survey,
        section=section_intro,
        label="Số CCCD/CMND",
        key="so_cccd",
        type_field=TYPE_FIELD.text,
        required=True,
        help_text="Nhập 9 hoặc 12 số",
        ordering=q_order
    )
    q_order += 1

    Question.objects.create(
        survey=survey,
        section=section_intro,
        label="Ngày tháng năm sinh",
        key="ngay_sinh",
        type_field=TYPE_FIELD.date,
        required=True,
        ordering=q_order
    )
    q_order += 1

    Question.objects.create(
        survey=survey,
        section=section_intro,
        label="Giới tính",
        key="gioi_tinh",
        type_field=TYPE_FIELD.radio,
        choices="Nam,Nữ",
        required=True,
        ordering=q_order
    )
    q_order += 1

    Question.objects.create(
        survey=survey,
        section=section_intro,
        label="Số điện thoại liên hệ",
        key="dien_thoai",
        type_field=TYPE_FIELD.text,
        required=True,
        ordering=q_order
    )
    q_order += 1

    Question.objects.create(
        survey=survey,
        section=section_intro,
        label="Địa chỉ thường trú",
        key="dia_chi_thuong_tru",
        type_field=TYPE_FIELD.text_area,
        required=True,
        help_text="Ghi theo CCCD",
        ordering=q_order
    )
    q_order += 1

    Question.objects.create(
        survey=survey,
        section=section_intro,
        label="Địa chỉ tạm trú (nếu có)",
        key="dia_chi_tam_tru",
        type_field=TYPE_FIELD.text_area,
        required=False,
        ordering=q_order
    )
    q_order += 1

    # Create dropdown for 262 groups (simplified for demo)
    to_dan_pho = ",".join([f"Tổ {i}" for i in range(1, 263)])
    Question.objects.create(
        survey=survey,
        section=section_intro,
        label="Tổ dân phố",
        key="to_dan_pho",
        type_field=TYPE_FIELD.select,
        choices=to_dan_pho,
        required=True,
        ordering=q_order
    )
    print(f"  ✓ Created {q_order} questions in Section 1")

    # SECTION 2: Choose number of GPLX
    print("\n📝 Creating questions for Section 2: Choose GPLX count...")
    
    q_count = Question.objects.create(
        survey=survey,
        section=section_choose_count,
        label="Anh/chị có bao nhiêu giấy phép lái xe mô tô đang giữ hoặc đã cấp trước đây?",
        key="so_luong_gplx",
        type_field=TYPE_FIELD.radio,
        choices="1 GPLX,2 GPLX,3 GPLX",
        required=True,
        enable_branching=True,
        ordering=1,
        help_text="Chọn số lượng GPLX bạn muốn khai báo"
    )
    
    # Set up branching logic
    q_count.branch_config = {
        "1_gplx": str(section_gplx1.id),
        "2_gplx": str(section_gplx1.id),  # Will go to GPLX1 first
        "3_gplx": str(section_gplx1.id)   # Will go to GPLX1 first
    }
    q_count.save()
    print("  ✓ Created branching question for GPLX count")

    # Helper function to create GPLX section questions
    def create_gplx_questions(section, gplx_number):
        print(f"\n📝 Creating questions for GPLX {gplx_number}...")
        q_order = 1
        
        Question.objects.create(
            survey=survey,
            section=section,
            label=f"Số GPLX {gplx_number}",
            key=f"so_gplx_{gplx_number}",
            type_field=TYPE_FIELD.text,
            required=True,
            ordering=q_order
        )
        q_order += 1

        Question.objects.create(
            survey=survey,
            section=section,
            label=f"Hạng GPLX {gplx_number}",
            key=f"hang_gplx_{gplx_number}",
            type_field=TYPE_FIELD.select,
            choices="A1,A2,A3,A4",
            required=True,
            ordering=q_order
        )
        q_order += 1

        Question.objects.create(
            survey=survey,
            section=section,
            label=f"Ngày cấp GPLX {gplx_number}",
            key=f"ngay_cap_{gplx_number}",
            type_field=TYPE_FIELD.date,
            required=True,
            ordering=q_order
        )
        q_order += 1

        Question.objects.create(
            survey=survey,
            section=section,
            label=f"Nơi cấp GPLX {gplx_number}",
            key=f"noi_cap_{gplx_number}",
            type_field=TYPE_FIELD.text,
            required=True,
            help_text="VD: Sở GTVT Đà Nẵng",
            ordering=q_order
        )
        q_order += 1

        Question.objects.create(
            survey=survey,
            section=section,
            label=f"Tình trạng GPLX {gplx_number}",
            key=f"tinh_trang_{gplx_number}",
            type_field=TYPE_FIELD.radio,
            choices="Còn sử dụng,Đã đổi sang PET,Mất,Hết hạn",
            required=True,
            ordering=q_order
        )
        q_order += 1

        Question.objects.create(
            survey=survey,
            section=section,
            label=f"Ảnh mặt trước GPLX {gplx_number}",
            key=f"anh_truoc_{gplx_number}",
            type_field=TYPE_FIELD.file,
            required=True,
            help_text="Upload ảnh định dạng .jpg hoặc .png, tối đa 5MB",
            ordering=q_order
        )
        q_order += 1

        Question.objects.create(
            survey=survey,
            section=section,
            label=f"Ảnh mặt sau GPLX {gplx_number}",
            key=f"anh_sau_{gplx_number}",
            type_field=TYPE_FIELD.file,
            required=False,
            help_text="Upload ảnh định dạng .jpg hoặc .png, tối đa 5MB",
            ordering=q_order
        )
        
        print(f"  ✓ Created {q_order} questions for GPLX {gplx_number}")

    # Create questions for each GPLX section
    create_gplx_questions(section_gplx1, 1)
    create_gplx_questions(section_gplx2, 2)
    create_gplx_questions(section_gplx3, 3)

    # SECTION 6: Commitment
    print("\n📝 Creating questions for Section 6: Commitment...")
    
    Question.objects.create(
        survey=survey,
        section=section_commitment,
        label="Cam kết",
        key="cam_ket",
        type_field=TYPE_FIELD.multi_select,
        choices="Tôi cam kết thông tin kê khai là đúng sự thật và đồng ý để Công an phường An Khê sử dụng dữ liệu này phục vụ công tác làm sạch, đồng bộ và quản lý giấy phép lái xe",
        required=True,
        ordering=1
    )
    print("  ✓ Created commitment checkbox")

    # Summary
    print("\n" + "="*70)
    print("✅ SURVEY CREATED SUCCESSFULLY!")
    print("="*70)
    print(f"\n📊 Summary:")
    print(f"   Survey: {survey.name}")
    print(f"   Slug: {survey.slug}")
    print(f"   Sections: {Section.objects.filter(survey=survey).count()}")
    print(f"   Questions: {Question.objects.filter(survey=survey).count()}")
    print(f"\n🌐 URLs:")
    print(f"   Admin Preview: http://127.0.0.1:8000/admin/survey/{survey.slug}/")
    print(f"   Fill Survey: http://127.0.0.1:8000/create/{survey.slug}/")
    print(f"   View Results: http://127.0.0.1:8000/detail/{survey.slug}/")
    print("\n" + "="*70)

if __name__ == '__main__':
    create_gplx_survey()
