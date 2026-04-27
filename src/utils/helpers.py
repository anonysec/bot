# src/utils/helpers.py - Utility functions for the application

def convert_traffic(value, unit='gb'):
    """Convert traffic between GB and MB"""
    if unit.lower() == 'gb':
        return value  # Already in GB
    elif unit.lower() == 'mb':
        return value / 1024  # MB to GB
    elif unit.lower() == 'bytes':
        return value / (1024**3)  # Bytes to GB
    return value

def format_traffic(bytes_value):
    """Format bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"

def parse_traffic_input(value, unit):
    """Parse traffic input from user (supports GB, MB)"""
    try:
        num = float(value)
        if unit.upper() in ['GB', 'G']:
            return num * 1024**3  # Convert to bytes
        elif unit.upper() in ['MB', 'M']:
            return num * 1024**2  # Convert to bytes
        elif unit.upper() in ['KB', 'K']:
            return num * 1024  # Convert to bytes
        elif unit.upper() in ['B']:
            return num  # Already bytes
        return num  # Default to bytes
    except ValueError:
        return None

def validate_email(email):
    """Validate email format"""
    import re
    pattern = r'^[^@]+@[^@]+\.[^@]+$'
    return bool(re.match(pattern, email))

def generate_uid():
    """Generate unique ID"""
    import uuid
    return str(uuid.uuid4())[:8]

def safe_divide(numerator, denominator):
    """Safe division avoiding division by zero"""
    if denominator == 0:
        return 0
    return numerator / denominator

def truncate_string(string, length=50):
    """Truncate string to length"""
    if len(string) > length:
        return string[:length-3] + "..."
    return string