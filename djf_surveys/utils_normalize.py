"""
Utility function to normalize choice text for branching keys
Must match JavaScript normalization in question_form_v2.html
"""

import unicodedata
import re

def normalize_choice_key(choice):
    """
    Normalize a choice string to use as branch_config key.
    Must match JavaScript normalization logic exactly.
    
    Example:
        "Hôm qua" -> "hom_qua"
        "Ngày mai" -> "ngay_mai"
    """
    # Lowercase
    text = choice.strip().lower()
    
    # Remove Vietnamese diacritics
    # Method 1: Using unicodedata (more reliable)
    text = unicodedata.normalize('NFD', text)
    text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')
    
    # Replace đ with d
    text = text.replace('đ', 'd').replace('Đ', 'd')
    
    # Replace spaces with underscores
    text = re.sub(r'\s+', '_', text)
    
    # Remove any non-alphanumeric except underscore
    text = re.sub(r'[^\w]', '', text)
    
    return text
