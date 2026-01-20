import base64

def encode_school_id(school_id: str) -> str:
    """Encodes a legacy school ID to the RMP base64 format if it's numeric."""
    if school_id.isdigit():
        encoded = base64.b64encode(f"School-{school_id}".encode()).decode()
        return encoded
    return school_id

def encode_teacher_id(teacher_id: int) -> str:
    """Encodes a legacy teacher ID to the RMP base64 format."""
    return base64.b64encode(f"Teacher-{teacher_id}".encode()).decode()
