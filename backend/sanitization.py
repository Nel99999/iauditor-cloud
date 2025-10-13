"""
Input Sanitization Utilities
Protects against XSS attacks by cleaning user inputs
"""
import bleach
from typing import Optional

# Allowed HTML tags (very restrictive for security)
ALLOWED_TAGS = []  # No HTML tags allowed
ALLOWED_ATTRIBUTES = {}  # No attributes allowed

def sanitize_input(text: Optional[str]) -> Optional[str]:
    """
    Sanitize text input to prevent XSS attacks
    Removes all HTML tags and dangerous content
    """
    if text is None:
        return None
    
    # Remove all HTML tags and clean the text
    cleaned = bleach.clean(
        text, 
        tags=ALLOWED_TAGS, 
        attributes=ALLOWED_ATTRIBUTES,
        strip=True  # Strip tags instead of escaping
    )
    
    return cleaned.strip()

def sanitize_dict(data: dict, fields: list) -> dict:
    """
    Sanitize specific fields in a dictionary
    
    Args:
        data: Dictionary containing user input
        fields: List of field names to sanitize
    
    Returns:
        Dictionary with sanitized fields
    """
    for field in fields:
        if field in data and isinstance(data[field], str):
            data[field] = sanitize_input(data[field])
    
    return data
