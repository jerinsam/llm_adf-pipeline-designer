import uuid
from datetime import datetime

def generate_name(prefix):
    """Generate a unique name with timestamp and prefix"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"{prefix}_{timestamp}_{unique_id}"

def validate_name(name):
    """Validate Azure resource naming conventions"""
    if not name:
        return False
    if len(name) > 260:
        return False
    if not name[0].isalpha():
        return False
    return True

def sanitize_name(name):
    """Sanitize name to follow Azure naming conventions"""
    # Remove invalid characters
    sanitized = ''.join(c for c in name if c.isalnum() or c in ['-', '_'])
    # Ensure it starts with a letter
    if sanitized and not sanitized[0].isalpha():
        sanitized = 'ADF' + sanitized
    # Limit length
    return sanitized[:260] if sanitized else 'ADF_Resource'