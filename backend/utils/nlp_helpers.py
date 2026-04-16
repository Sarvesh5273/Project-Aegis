import re

def apply_regex_fallbacks(text: str) -> tuple:
    """
    Executes Layer 3 deterministic regex fallbacks.
    Returns (sanitized_text, regex_redaction_map) so the frontend
    can highlight regex-caught tokens alongside NER/LLM tokens.
    """
    regex_map = {}

    def replace_and_record(pattern, token, t, flags=0):
        matches = re.findall(pattern, t, flags)
        for m in matches:
            # findall returns tuples for groups — take first element
            key = m if isinstance(m, str) else m[0]
            if key:
                regex_map[key] = token
        return re.sub(pattern, token, t, flags=flags)

    # Catches standard emails
    text = replace_and_record(r'[\w\.-]+@[\w\.-]+', '[EMAIL_REDACTED]', text)

    # Myanmar & International Phone Numbers (+95-9-555-0192)
    text = replace_and_record(r'(\+?\d[\d\s\-\(\)\.]{6,18}\d)', '[PHONE_REDACTED]', text)

    # IPv4 Addresses
    text = replace_and_record(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', '[IP_REDACTED]', text)

    # GPS Coordinate Pairs (16.8059 N, 96.1561 E)
    text = replace_and_record(r'\d{1,3}(\.\d+)?°?[NS],\s*\d{1,3}(\.\d+)?°?[EW]', '[COORDS_REDACTED]', text)

    # Standalone decimal degree values (96.1561 E)
    text = replace_and_record(r'\b\d{1,3}\.\d{2,6}\s*[NSEW]\b', '[COORDS_REDACTED]', text)

    return text, regex_map