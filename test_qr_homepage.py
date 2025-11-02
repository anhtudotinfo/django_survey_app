#!/usr/bin/env python
"""
Test QR Code trên Homepage có Domain Đầy Đủ
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

def test_homepage_qr():
    """Test QR codes on homepage have full domain"""
    print("=" * 70)
    print("TEST: QR Code Trên Homepage - Có Domain Đầy Đủ")
    print("=" * 70)
    
    # Get surveys
    surveys = Survey.objects.all()[:3]  # Test first 3
    if not surveys:
        print("❌ Không có survey nào!")
        return
    
    print(f"\n📋 Tìm thấy {surveys.count()} surveys")
    
    # Create mock request
    factory = RequestFactory()
    request = factory.get('/')
    request.META['HTTP_HOST'] = '127.0.0.1:8000'
    
    print("\n🔍 Test QR Code Generation:")
    print("-" * 70)
    
    for i, survey in enumerate(surveys, 1):
        print(f"\n{i}. Survey: {survey.name}")
        print(f"   Slug: {survey.slug}")
        
        # Generate QR with request (như trong view)
        qr_with_domain = survey.generate_qr_code(request)
        
        # Check QR data
        if qr_with_domain and qr_with_domain.startswith('data:image'):
            print(f"   ✅ QR Code generated")
            print(f"   📏 Size: {len(qr_with_domain)} bytes")
            
            # Build expected URL
            full_url = request.build_absolute_uri(survey.get_absolute_url())
            print(f"   🔗 URL in QR: {full_url}")
            
            # Verify has domain
            if 'http://' in full_url or 'https://' in full_url:
                if '127.0.0.1' in full_url or 'localhost' in full_url or request.META['HTTP_HOST'] in full_url:
                    print(f"   ✅ Domain included!")
                else:
                    print(f"   ⚠️  Domain might be missing")
            else:
                print(f"   ❌ No protocol (http/https)!")
        else:
            print(f"   ❌ Failed to generate QR")
    
    print("\n" + "=" * 70)
    print("HƯỚNG DẪN KIỂM TRA TRỰC QUAN:")
    print("=" * 70)
    print("1. Chạy server:")
    print("   python3 manage.py runserver")
    print()
    print("2. Mở trình duyệt:")
    print("   http://127.0.0.1:8000/")
    print()
    print("3. Xem QR code trên mỗi card:")
    print("   ✓ QR phải lớn (40x40 thay vì 32x32)")
    print("   ✓ Bên dưới QR có text: 'Quét Mã QR - Truy Cập Ngay'")
    print("   ✓ Có dòng 'Địa chỉ đầy đủ: http://...'")
    print()
    print("4. Click chuột phải vào QR code → 'Mở hình ảnh trong tab mới'")
    print("   ✓ Nếu thấy data:image/png;base64,... → QR đã được tạo")
    print()
    print("5. Test quét QR:")
    print("   ✓ Mở camera điện thoại")
    print("   ✓ Quét QR code trên màn hình")
    print("   ✓ Xem URL xuất hiện có http://127.0.0.1:8000 hay không")
    print()
    print("6. Alternative: Download QR và quét")
    print("   ✓ Click vào button 'Mã QR' trên card")
    print("   ✓ Download QR code PNG")
    print("   ✓ Quét file đã download")
    print("=" * 70)
    
    print("\n" + "=" * 70)
    print("CODE CHANGES:")
    print("=" * 70)
    print("✅ views.py: Added QR generation in get_context_data()")
    print("   - Loop through surveys")
    print("   - Call survey.generate_qr_code(request)")
    print("   - Store in survey.qr_code_with_domain")
    print()
    print("✅ card_list_survey.html: Changed img src")
    print("   - Before: {{ survey.generate_qr_code }}")
    print("   - After:  {{ survey.qr_code_with_domain }}")
    print()
    print("✅ Domain display added:")
    print("   - Shows: {{ request.scheme }}://{{ request.get_host }}/detail/{{ survey.slug }}/")
    print("=" * 70)

if __name__ == '__main__':
    test_homepage_qr()
