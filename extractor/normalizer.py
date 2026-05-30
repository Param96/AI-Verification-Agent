import re

def normalize_text(text: str) -> str:
    """Basic text normalization: lowercase and strip."""
    if not text:
        return ""
    return str(text).lower().strip()

def normalize_course_type(course_type: str) -> str:
    """Normalizes course types based on standard equivalents."""
    val = normalize_text(course_type)
    
    if val in ["pg diploma", "post-graduate diploma", "postgraduate diploma"]:
        return "Post Graduate Diploma"
    elif val in ["master's degree", "master degree", "masters"]:
        return "Masters"
    elif val in ["bachelor's degree", "bachelor degree", "bachelors"]:
        return "Bachelors"
    elif val in ["pg certificate", "post-graduate certificate", "postgraduate certificate"]:
        return "Post Graduate Certificate"
    elif "certificate" in val:
        return "Certificate"
    elif "diploma" in val:
        return "Diploma"
        
    return course_type.title()

def extract_numeric_fee(fee_str: str) -> float:
    """Extracts numeric value from a fee string, ignoring currencies."""
    if not fee_str:
        return 0.0
    # Find all digits and optional decimal
    matches = re.findall(r'\d+(?:,\d+)*(?:\.\d+)?', str(fee_str))
    if matches:
        return float(matches[0].replace(',', ''))
    return 0.0

def normalize_duration_to_months(duration_str: str) -> int:
    """Converts a duration string to an approximate integer in months."""
    if not duration_str:
        return 0
    val = normalize_text(duration_str)
    
    months = 0
    # Look for years
    year_match = re.search(r'(\d+(?:\.\d+)?)\s*y', val)
    if year_match:
        months += int(float(year_match.group(1)) * 12)
        
    # Look for months
    month_match = re.search(r'(\d+(?:\.\d+)?)\s*m', val)
    if month_match:
        months += int(float(month_match.group(1)))
        
    # Look for weeks
    week_match = re.search(r'(\d+(?:\.\d+)?)\s*w', val)
    if week_match:
        months += int(float(week_match.group(1)) / 4.33)
        
    return months
