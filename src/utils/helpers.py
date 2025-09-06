import hashlib

def anonymize_id(student_id: str) -> str:
    return hashlib.sha256(student_id.encode("utf-8")).hexdigest()[:10]