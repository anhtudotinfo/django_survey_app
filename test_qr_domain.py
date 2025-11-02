#!/usr/bin/env python
"""
Test QR Code với Domain Đầy Đủ
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moi.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.test import RequestFactory
from djf_surveys.models import Survey

def test_qr_with_domain():
    """Test QR code generation with full domain"""
    print("=" * 70)
    print("TEST: QR Code với Domain Đầy Đủ")
    print("=" * 70)
    
    # Get first survey
    survey = Survey.objects.first()
    if not survey:
        print("❌ Không có survey nào. Hãy tạo survey trước!")
        return
    
    print(f"\n📋 Survey: {survey.name}")
    print(f"   Slug: {survey.slug}")
    
    # Test without request (fallback)
    print("\n🔍 Test 1: Tạo QR Code không có request (fallback)...")
    qr_data_no_req = survey.generate_qr_code()
    if qr_data_no_req and qr_data_no_req.startswith('data:image'):
        print("✅ QR Code tạo được (relative URL)")
    else:
        print("❌ QR Code không được tạo!")
    
    # Show what URL should be
    print(f"\n🔗 Relative URL: {survey.get_absolute_url()}")
    print(f"   → Khi có request, sẽ thành: http://domain{survey.get_absolute_url()}")
    
    print("\n" + "=" * 70)
    print("HƯỚNG DẪN KIỂM TRA:")
    print("=" * 70)
    print("1. Chạy server: python3 manage.py runserver")
    print(f"2. Vào: http://127.0.0.1:8000/qr/{survey.slug}/")
    print("3. Kiểm tra:")
    print("   ✓ Hộp màu tím hiển thị domain")
    print("   ✓ Mã QR hiển thị ở giữa")
    print("   ✓ Có nút Download QR Code")
    print("   ✓ Có hướng dẫn in ấn màu xanh")
    print("\n4. Download QR và test:")
    print("   ✓ Click 'Download QR Code'")
    print("   ✓ Lưu file PNG")
    print("   ✓ Quét bằng điện thoại")
    print("   ✓ Verify mở đúng survey")
    print("\n5. In ra giấy:")
    print("   ✓ In size 10cm x 10cm")
    print("   ✓ Giấy 200gsm")
    print("   ✓ Cán màng bóng")
    print("=" * 70)

if __name__ == '__main__':
    test_qr_with_domain()
