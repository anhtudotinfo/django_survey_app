#!/usr/bin/env python3
"""
Test script for Question Validation functionality
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moi.settings')
django.setup()

from djf_surveys.models import Question, Survey, TYPE_FIELD


def test_validation_defaults():
    """Test default validation values"""
    print("=" * 60)
    print("TEST 1: Validation Defaults")
    print("=" * 60)
    
    # Create a test question
    survey = Survey.objects.first()
    if not survey:
        print("❌ No surveys found")
        return False
    
    question = Question(
        survey=survey,
        label="Test Question",
        type_field=TYPE_FIELD.text,
        required=True
    )
    
    # Test defaults
    defaults = question.get_validation_defaults()
    print(f"✓ Text field defaults: {defaults}")
    
    assert defaults['min_length'] == 0, "Text min_length should be 0"
    assert defaults['max_length'] == 500, "Text max_length should be 500"
    assert defaults['regex_pattern'] is None, "Text regex should be None"
    
    # Test other field types
    question.type_field = TYPE_FIELD.text_area
    defaults = question.get_validation_defaults()
    print(f"✓ Text area defaults: {defaults}")
    assert defaults['max_length'] == 5000, "Text area max should be 5000"
    
    question.type_field = TYPE_FIELD.email
    defaults = question.get_validation_defaults()
    print(f"✓ Email defaults: {defaults}")
    assert defaults['max_length'] == 254, "Email max should be 254"
    assert defaults['regex_pattern'] is not None, "Email should have regex"
    
    print("✅ Validation Defaults: PASSED\n")
    return True


def test_effective_values():
    """Test effective validation values (custom or default)"""
    print("=" * 60)
    print("TEST 2: Effective Values")
    print("=" * 60)
    
    survey = Survey.objects.first()
    if not survey:
        print("❌ No surveys found")
        return False
    
    question = Question(
        survey=survey,
        label="Test Question",
        type_field=TYPE_FIELD.text,
        required=True
    )
    
    # Test with defaults (no custom values)
    print("Testing with defaults...")
    assert question.get_effective_min_length() == 0
    assert question.get_effective_max_length() == 500
    assert question.get_effective_regex_pattern() is None
    print("✓ Default values work correctly")
    
    # Test with custom values
    print("Testing with custom values...")
    question.min_length = 10
    question.max_length = 100
    question.regex_pattern = "^[A-Z]+$"
    
    assert question.get_effective_min_length() == 10
    assert question.get_effective_max_length() == 100
    assert question.get_effective_regex_pattern() == "^[A-Z]+$"
    print("✓ Custom values override defaults")
    
    print("✅ Effective Values: PASSED\n")
    return True


def test_answer_validation():
    """Test answer validation logic"""
    print("=" * 60)
    print("TEST 3: Answer Validation")
    print("=" * 60)
    
    survey = Survey.objects.first()
    if not survey:
        print("❌ No surveys found")
        return False
    
    question = Question(
        survey=survey,
        label="Test Question",
        type_field=TYPE_FIELD.text,
        required=True,
        min_length=5,
        max_length=20
    )
    
    # Test valid answer
    is_valid, error = question.validate_answer("Hello World")
    assert is_valid, "Valid answer should pass"
    print(f"✓ Valid answer: 'Hello World' - PASSED")
    
    # Test too short
    is_valid, error = question.validate_answer("Hi")
    assert not is_valid, "Too short should fail"
    assert "Minimum" in error or "minimum" in error.lower()
    print(f"✓ Too short: 'Hi' - FAILED (as expected): {error}")
    
    # Test too long
    is_valid, error = question.validate_answer("This is a very long text that exceeds the limit")
    assert not is_valid, "Too long should fail"
    assert "Maximum" in error or "maximum" in error.lower()
    print(f"✓ Too long - FAILED (as expected): {error}")
    
    # Test with regex
    question.regex_pattern = "^[A-Z]+$"
    question.validation_message = "Only uppercase letters allowed"
    
    is_valid, error = question.validate_answer("HELLO")
    assert is_valid, "HELLO should pass uppercase-only regex"
    print(f"✓ Regex match: 'HELLO' - PASSED")
    
    is_valid, error = question.validate_answer("Hello")
    assert not is_valid, "Hello should fail uppercase-only regex"
    assert error == "Only uppercase letters allowed"
    print(f"✓ Regex fail: 'Hello' - FAILED (as expected): {error}")
    
    print("✅ Answer Validation: PASSED\n")
    return True


def test_validation_rules_dict():
    """Test validation rules dictionary output"""
    print("=" * 60)
    print("TEST 4: Validation Rules Dict")
    print("=" * 60)
    
    survey = Survey.objects.first()
    if not survey:
        print("❌ No surveys found")
        return False
    
    question = Question(
        survey=survey,
        label="Test Question",
        type_field=TYPE_FIELD.text,
        required=True,
        min_length=10,
        max_length=100,
        regex_pattern="^[a-zA-Z0-9]+$",
        validation_message="Alphanumeric only"
    )
    
    rules = question.get_validation_rules_dict()
    
    print("Validation rules dict:")
    for key, value in rules.items():
        print(f"  {key}: {value}")
    
    assert rules['min_length'] == 10
    assert rules['max_length'] == 100
    assert rules['regex_pattern'] == "^[a-zA-Z0-9]+$"
    assert rules['validation_message'] == "Alphanumeric only"
    assert rules['required'] == True
    
    print("✅ Validation Rules Dict: PASSED\n")
    return True


def test_field_type_compatibility():
    """Test validation compatibility with different field types"""
    print("=" * 60)
    print("TEST 5: Field Type Compatibility")
    print("=" * 60)
    
    survey = Survey.objects.first()
    if not survey:
        print("❌ No surveys found")
        return False
    
    # Test field types that support validation
    text_types = [TYPE_FIELD.text, TYPE_FIELD.text_area, TYPE_FIELD.email, 
                  TYPE_FIELD.url, TYPE_FIELD.number]
    
    for field_type in text_types:
        question = Question(
            survey=survey,
            label="Test",
            type_field=field_type,
            min_length=5,
            max_length=50
        )
        defaults = question.get_validation_defaults()
        print(f"✓ Field type {field_type}: {defaults}")
    
    # Test field types that don't support validation
    non_text_types = [TYPE_FIELD.radio, TYPE_FIELD.select, 
                     TYPE_FIELD.multi_select, TYPE_FIELD.rating, TYPE_FIELD.file]
    
    for field_type in non_text_types:
        question = Question(
            survey=survey,
            label="Test",
            type_field=field_type
        )
        is_valid, error = question.validate_answer("anything")
        assert is_valid, f"Field type {field_type} should skip validation"
        print(f"✓ Field type {field_type}: Skips validation (correct)")
    
    print("✅ Field Type Compatibility: PASSED\n")
    return True


def test_regex_patterns():
    """Test common regex patterns"""
    print("=" * 60)
    print("TEST 6: Common Regex Patterns")
    print("=" * 60)
    
    survey = Survey.objects.first()
    if not survey:
        print("❌ No surveys found")
        return False
    
    test_cases = [
        {
            'pattern': r'^\d+$',
            'valid': ['123', '0', '999999'],
            'invalid': ['abc', '12.3', 'a123'],
            'name': 'Numbers only'
        },
        {
            'pattern': r'^[A-Z]+$',
            'valid': ['HELLO', 'ABC', 'Z'],
            'invalid': ['hello', 'Hello', '123'],
            'name': 'Uppercase only'
        },
        {
            'pattern': r'^[a-zA-Z0-9]+$',
            'valid': ['Hello123', 'ABC', '123'],
            'invalid': ['hello world', 'test@', 'abc-def'],
            'name': 'Alphanumeric'
        },
        {
            'pattern': r'^\d{4}-\d{2}-\d{2}$',
            'valid': ['2025-01-02', '1990-12-31'],
            'invalid': ['2025/01/02', '25-01-02', 'invalid'],
            'name': 'Date (YYYY-MM-DD)'
        },
    ]
    
    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        print(f"Pattern: {test_case['pattern']}")
        
        question = Question(
            survey=survey,
            label="Test",
            type_field=TYPE_FIELD.text,
            regex_pattern=test_case['pattern']
        )
        
        # Test valid cases
        for value in test_case['valid']:
            is_valid, error = question.validate_answer(value)
            if is_valid:
                print(f"  ✓ '{value}' - Valid")
            else:
                print(f"  ❌ '{value}' - Should be valid but failed: {error}")
                return False
        
        # Test invalid cases
        for value in test_case['invalid']:
            is_valid, error = question.validate_answer(value)
            if not is_valid:
                print(f"  ✓ '{value}' - Invalid (as expected)")
            else:
                print(f"  ❌ '{value}' - Should be invalid but passed")
                return False
    
    print("\n✅ Common Regex Patterns: PASSED\n")
    return True


def run_all_tests():
    """Run all validation tests"""
    print("\n" + "=" * 60)
    print("QUESTION VALIDATION TEST SUITE")
    print("=" * 60 + "\n")
    
    results = []
    
    results.append(("Validation Defaults", test_validation_defaults()))
    results.append(("Effective Values", test_effective_values()))
    results.append(("Answer Validation", test_answer_validation()))
    results.append(("Validation Rules Dict", test_validation_rules_dict()))
    results.append(("Field Type Compatibility", test_field_type_compatibility()))
    results.append(("Common Regex Patterns", test_regex_patterns()))
    
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
        print("\n🎉 All validation tests passed successfully!")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(run_all_tests())
