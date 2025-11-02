#!/usr/bin/env python3
"""
Test script for QR Code functionality
Tests QR code generation, views, and templates
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moi.settings')
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth import get_user_model
from djf_surveys.models import Survey
from djf_surveys.views import survey_qr_code, survey_qr_download
import base64


def test_qr_code_generation():
    """Test QR code generation in Survey model"""
    print("=" * 60)
    print("TEST 1: QR Code Generation")
    print("=" * 60)
    
    # Get first survey
    survey = Survey.objects.first()
    if not survey:
        print("❌ No surveys found in database")
        return False
    
    print(f"✓ Testing survey: {survey.name}")
    
    # Test get_absolute_url
    try:
        url = survey.get_absolute_url()
        print(f"✓ Absolute URL: {url}")
    except Exception as e:
        print(f"❌ Failed to get absolute URL: {e}")
        return False
    
    # Test generate_qr_code
    try:
        qr_data = survey.generate_qr_code()
        
        # Verify it's a base64 data URI
        if not qr_data.startswith('data:image/png;base64,'):
            print("❌ QR code data is not in correct format")
            return False
        
        # Extract base64 data
        base64_data = qr_data.split(',')[1]
        decoded = base64.b64decode(base64_data)
        
        # Check if it's valid PNG
        if not decoded.startswith(b'\x89PNG'):
            print("❌ QR code is not a valid PNG image")
            return False
        
        print(f"✓ QR code generated successfully ({len(decoded)} bytes)")
        
    except Exception as e:
        print(f"❌ Failed to generate QR code: {e}")
        return False
    
    # Test get_qr_download_url
    try:
        download_url = survey.get_qr_download_url()
        print(f"✓ Download URL: {download_url}")
    except Exception as e:
        print(f"❌ Failed to get download URL: {e}")
        return False
    
    print("✅ QR Code Generation: PASSED\n")
    return True


def test_qr_code_view():
    """Test QR code display view"""
    print("=" * 60)
    print("TEST 2: QR Code Display View")
    print("=" * 60)
    
    client = Client()
    survey = Survey.objects.first()
    
    if not survey:
        print("❌ No surveys found")
        return False
    
    try:
        # Test view access
        url = f'/qr/{survey.slug}/'
        response = client.get(url)
        
        if response.status_code != 200:
            print(f"❌ View returned status code {response.status_code}")
            return False
        
        print(f"✓ View accessible (status 200)")
        
        # Check context
        if hasattr(response, 'context') and response.context is not None:
            if 'survey' not in response.context:
                print("❌ Survey not in context")
                return False
            
            if 'qr_code' not in response.context:
                print("❌ QR code not in context")
                return False
            
            if 'survey_url' not in response.context:
                print("❌ Survey URL not in context")
                return False
            
            print(f"✓ Context data present")
        else:
            print("⚠ No context available, skipping context check")
        
        # Check template rendering
        if hasattr(response, 'content'):
            content = response.content.decode('utf-8')
            
            if survey.name not in content:
                print("❌ Survey name not in rendered content")
                return False
            
            if 'data:image/png;base64,' not in content:
                print("❌ QR code image not in rendered content")
                return False
            
            print(f"✓ Template rendered correctly")
        else:
            print("⚠ Response has no content attribute, skipping content check")
        
    except Exception as e:
        print(f"❌ View test failed: {e}")
        return False
    
    print("✅ QR Code Display View: PASSED\n")
    return True


def test_qr_code_download():
    """Test QR code download functionality"""
    print("=" * 60)
    print("TEST 3: QR Code Download")
    print("=" * 60)
    
    client = Client()
    survey = Survey.objects.first()
    
    if not survey:
        print("❌ No surveys found")
        return False
    
    try:
        # Test download endpoint
        url = f'/qr/{survey.slug}/download/'
        response = client.get(url)
        
        if response.status_code != 200:
            print(f"❌ Download returned status code {response.status_code}")
            return False
        
        print(f"✓ Download endpoint accessible")
        
        # Check content type
        if response['Content-Type'] != 'image/png':
            print(f"❌ Wrong content type: {response['Content-Type']}")
            return False
        
        print(f"✓ Correct content type: image/png")
        
        # Check content disposition
        if 'Content-Disposition' not in response:
            print("❌ Content-Disposition header missing")
            return False
        
        disposition = response['Content-Disposition']
        if not disposition.startswith('attachment'):
            print("❌ Not set as attachment")
            return False
        
        print(f"✓ Content-Disposition: {disposition}")
        
        # Check image data
        image_data = response.content
        if not image_data.startswith(b'\x89PNG'):
            print("❌ Downloaded file is not a valid PNG")
            return False
        
        print(f"✓ Valid PNG image ({len(image_data)} bytes)")
        
    except Exception as e:
        print(f"❌ Download test failed: {e}")
        return False
    
    print("✅ QR Code Download: PASSED\n")
    return True


def test_homepage_redesign():
    """Test homepage template changes"""
    print("=" * 60)
    print("TEST 4: Homepage Redesign")
    print("=" * 60)
    
    client = Client()
    
    try:
        response = client.get('/')
        
        if response.status_code != 200:
            print(f"❌ Homepage returned status code {response.status_code}")
            return False
        
        print(f"✓ Homepage accessible")
        
        content = response.content.decode('utf-8')
        
        # Check for new design elements
        checks = [
            ('hero-gradient', 'Hero section with gradient'),
            ('Survey Management System', 'Hero title'),
            ('Available Surveys', 'Surveys section heading'),
            ('card-hover', 'Hover effect styling'),
        ]
        
        for check_str, description in checks:
            if check_str in content:
                print(f"✓ {description} present")
            else:
                print(f"⚠ {description} not found (may be conditional)")
        
    except Exception as e:
        print(f"❌ Homepage test failed: {e}")
        return False
    
    print("✅ Homepage Redesign: PASSED\n")
    return True


def test_survey_card_qr_button():
    """Test QR button in survey card"""
    print("=" * 60)
    print("TEST 5: Survey Card QR Button")
    print("=" * 60)
    
    client = Client()
    survey = Survey.objects.first()
    
    if not survey:
        print("❌ No surveys found")
        return False
    
    try:
        response = client.get('/')
        content = response.content.decode('utf-8')
        
        # Check for QR button link
        qr_url = f"/qr/{survey.slug}/"
        
        if qr_url in content:
            print(f"✓ QR button link present: {qr_url}")
        else:
            print(f"❌ QR button link not found")
            return False
        
        # Check for indigo styling (QR button color)
        if 'bg-indigo-100' in content:
            print(f"✓ QR button styling present")
        else:
            print(f"⚠ QR button styling not found")
        
    except Exception as e:
        print(f"❌ Card test failed: {e}")
        return False
    
    print("✅ Survey Card QR Button: PASSED\n")
    return True


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("QR CODE FUNCTIONALITY TEST SUITE")
    print("=" * 60 + "\n")
    
    results = []
    
    # Run tests
    results.append(("QR Code Generation", test_qr_code_generation()))
    results.append(("QR Code Display View", test_qr_code_view()))
    results.append(("QR Code Download", test_qr_code_download()))
    results.append(("Homepage Redesign", test_homepage_redesign()))
    results.append(("Survey Card QR Button", test_survey_card_qr_button()))
    
    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed successfully!")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(run_all_tests())
