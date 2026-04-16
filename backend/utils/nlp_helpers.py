import re

def apply_regex_fallbacks(text: str) -> str:
    """
    Executes Layer 3 deterministic regex fallbacks.
    Crucial for protecting specific data formats (like Myanmar phone numbers)
    before they ever touch a generative model.
    """
    # Catches standard emails
    text = re.sub(r'[\w\.-]+@[\w\.-]+', '[EMAIL_REDACTED]', text)
    
    # CRITICAL FIX: Myanmar & International Phone Regex (+95-9-555-0192)
    text = re.sub(r'(\+?\d[\d\s\-\(\)\.]{6,18}\d)', '[PHONE_REDACTED]', text)
    
    # IPv4 Addresses
    text = re.sub(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', '[IP_REDACTED]', text)
    
    # GPS Coordinates
    text = re.sub(r'\d{1,3}(\.\d+)?°?[NS],\s*\d{1,3}(\.\d+)?°?[EW]', '[COORDS_REDACTED]', text)
    
    return text