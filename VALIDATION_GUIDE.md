# Question Validation Rules Guide

## Overview
The survey system now supports customizable validation rules for questions, including minimum/maximum length constraints and regex pattern matching.

## Features

### Validation Fields

#### 1. **Minimum Length** (`min_length`)
- Specifies the minimum number of characters required
- Applies to: Text, Text Area, URL, Email fields
- Default values:
  - Text: 0 characters
  - Text Area: 0 characters
  - URL: 0 characters
  - Email: 0 characters

#### 2. **Maximum Length** (`max_length`)
- Specifies the maximum number of characters allowed
- Applies to: Text, Text Area, URL, Email fields
- Default values:
  - Text: 500 characters
  - Text Area: 5000 characters
  - URL: 2048 characters
  - Email: 254 characters

#### 3. **Regex Pattern** (`regex_pattern`)
- Regular expression pattern for custom validation
- Applies to: Text, Text Area, Number, URL, Email fields
- Default patterns:
  - Number: `^\d+$` (digits only)
  - URL: `^https?://.*` (valid URL format)
  - Email: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`
  - Others: None

#### 4. **Validation Message** (`validation_message`)
- Custom error message shown when validation fails
- Applies to: All field types with validation
- Default: "Invalid format" or field-specific message

## Usage

### In Admin Interface

1. **Create/Edit Question**
   - Navigate to survey admin
   - Create or edit a question
   - Scroll to "Validation Rules" section

2. **Set Validation Rules**
   - **Minimum Length**: Enter minimum character count
   - **Maximum Length**: Enter maximum character count
   - **Regex Pattern**: Enter regex pattern
   - **Validation Message**: Enter custom error message

3. **Leave Blank for Defaults**
   - Empty fields will use default values
   - Defaults depend on field type

### Examples

#### Example 1: Phone Number Validation
```
Field Type: Text
Min Length: 10
Max Length: 15
Regex Pattern: ^\+?[\d\s-()]+$
Validation Message: Please enter a valid phone number
```

#### Example 2: Postal Code
```
Field Type: Text
Min Length: 5
Max Length: 10
Regex Pattern: ^\d{5}(-\d{4})?$
Validation Message: Enter a valid postal code (12345 or 12345-6789)
```

#### Example 3: Username
```
Field Type: Text
Min Length: 3
Max Length: 20
Regex Pattern: ^[a-zA-Z0-9_]+$
Validation Message: Username must be 3-20 characters, alphanumeric and underscore only
```

#### Example 4: Limited Text Area
```
Field Type: Text Area
Min Length: 50
Max Length: 500
Regex Pattern: (leave blank)
Validation Message: Please provide a detailed response (50-500 characters)
```

#### Example 5: URL with HTTPS Only
```
Field Type: URL
Min Length: 10
Max Length: 2048
Regex Pattern: ^https://.*
Validation Message: Only secure HTTPS URLs are allowed
```

## Common Regex Patterns

### Basic Patterns

| Pattern | Description | Example |
|---------|-------------|---------|
| `^\d+$` | Only numbers | 12345 |
| `^[A-Z]+$` | Only uppercase letters | HELLO |
| `^[a-z]+$` | Only lowercase letters | hello |
| `^[a-zA-Z]+$` | Only letters | Hello |
| `^[a-zA-Z0-9]+$` | Alphanumeric only | Hello123 |
| `^[a-zA-Z0-9_-]+$` | Alphanumeric with underscore and dash | hello_world-123 |

### Advanced Patterns

| Pattern | Description | Example |
|---------|-------------|---------|
| `^\d{4}-\d{2}-\d{2}$` | Date (YYYY-MM-DD) | 2025-01-02 |
| `^\d{2}/\d{2}/\d{4}$` | Date (DD/MM/YYYY) | 02/01/2025 |
| `^\+?[\d\s-()]+$` | Phone number | +1 (555) 123-4567 |
| `^\d{5}(-\d{4})?$` | US ZIP code | 12345 or 12345-6789 |
| `^[A-Z]{2}\d{2}\s?\d{4}$` | UK postcode | SW1A 1AA |
| `^#[0-9A-Fa-f]{6}$` | Hex color code | #FF5733 |
| `^https?://[\w\-\.]+\.\w{2,}.*$` | URL | https://example.com |

### Specialized Patterns

```regex
# Credit card (basic format)
^\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}$

# IPv4 address
^(\d{1,3}\.){3}\d{1,3}$

# MAC address
^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$

# Bitcoin address
^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$

# Strong password (min 8 chars, uppercase, lowercase, number)
^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$
```

## Default Validation Values

### By Field Type

| Field Type | Min Length | Max Length | Regex Pattern |
|------------|------------|------------|---------------|
| Text | 0 | 500 | None |
| Text Area | 0 | 5000 | None |
| Number | N/A | N/A | `^\d+$` |
| URL | 0 | 2048 | `^https?://.*` |
| Email | 0 | 254 | Email regex |
| Date | N/A | N/A | `^\d{4}-\d{2}-\d{2}$` |
| Radio | N/A | N/A | None |
| Select | N/A | N/A | None |
| Multi-Select | N/A | N/A | None |
| Rating | N/A | N/A | None |
| File | N/A | N/A | None |

## Model Methods

### Question Model Methods

```python
# Get default validation values
defaults = question.get_validation_defaults()

# Get effective values (custom or default)
min_len = question.get_effective_min_length()
max_len = question.get_effective_max_length()
pattern = question.get_effective_regex_pattern()

# Validate an answer
is_valid, error_msg = question.validate_answer(value)

# Get validation rules as dict
rules = question.get_validation_rules_dict()
```

### Usage Example

```python
from djf_surveys.models import Question

question = Question.objects.get(id=1)

# Check validation rules
rules = question.get_validation_rules_dict()
print(rules)
# Output: {
#     'min_length': 10,
#     'max_length': 100,
#     'regex_pattern': '^[a-zA-Z0-9]+$',
#     'validation_message': 'Alphanumeric only',
#     'required': True
# }

# Validate an answer
value = "Hello123"
is_valid, error = question.validate_answer(value)
if is_valid:
    print("Valid!")
else:
    print(f"Invalid: {error}")
```

## Frontend Integration

### Form Validation

Forms automatically apply validation rules based on question settings:

```python
# In forms.py - automatically applied
validators = []

min_len = question.get_effective_min_length()
if min_len:
    validators.append(MinLengthValidator(min_len))

max_len = question.get_effective_max_length()
if max_len:
    validators.append(MaxLengthValidator(max_len))

regex = question.get_effective_regex_pattern()
if regex:
    validators.append(RegexValidator(regex, message=question.validation_message))
```

### Display in Templates

Validation rules are shown in admin interface:

- Green section with "Validation Rules" header
- Four fields: Min Length, Max Length, Regex Pattern, Validation Message
- Regex examples provided
- Default values info displayed

## Best Practices

### 1. **Start with Defaults**
- Leave fields blank to use sensible defaults
- Customize only when needed

### 2. **Test Regex Patterns**
- Test patterns before deploying
- Use tools like regex101.com
- Provide clear error messages

### 3. **User-Friendly Messages**
- Write clear validation messages
- Explain what format is expected
- Provide examples

### 4. **Avoid Over-Validation**
- Don't make it too restrictive
- Consider edge cases
- Allow reasonable flexibility

### 5. **Consider Field Type**
- Different types have different defaults
- URL/Email have built-in validation
- Numbers use regex for format

## Troubleshooting

### Issue: Regex Not Working
**Cause**: Invalid regex syntax
**Solution**: Test regex pattern, check escaping

### Issue: Validation Too Strict
**Cause**: Min/Max lengths too restrictive
**Solution**: Adjust limits or remove them

### Issue: Custom Message Not Showing
**Cause**: Message field empty
**Solution**: Enter custom message or use default

### Issue: Validation Bypassed
**Cause**: Field type doesn't support validation
**Solution**: Check field type compatibility

## Security Considerations

### DO:
- ✅ Validate user input
- ✅ Use appropriate length limits
- ✅ Sanitize regex patterns
- ✅ Provide clear error messages

### DON'T:
- ❌ Trust client-side validation only
- ❌ Allow extremely long inputs
- ❌ Use complex regex that causes DoS
- ❌ Expose sensitive info in errors

## API Reference

### Question Model Fields

```python
class Question(BaseModel):
    # ... existing fields ...
    
    min_length = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Minimum number of characters required"
    )
    
    max_length = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Maximum number of characters allowed"
    )
    
    regex_pattern = models.CharField(
        max_length=500, null=True, blank=True,
        help_text="Regular expression pattern for validation"
    )
    
    validation_message = models.CharField(
        max_length=200, null=True, blank=True,
        help_text="Custom error message"
    )
```

### Method Signatures

```python
def get_validation_defaults() -> dict
def get_effective_min_length() -> int or None
def get_effective_max_length() -> int or None
def get_effective_regex_pattern() -> str or None
def validate_answer(value: any) -> tuple[bool, str or None]
def get_validation_rules_dict() -> dict
```

## Migration

The validation fields were added in migration `0026_alter_answer_options_...`.

No data migration needed - all existing questions use default values.

## Version History

- **v1.0** (2025-01-02): Initial implementation
  - Added 4 validation fields
  - Implemented default values
  - Added form validation
  - Updated admin interface

---

**Questions or issues?** Contact system administrator or check Django logs.
