from datetime import datetime

def serialize_datetime(dt: datetime) -> str:
    """Convert datetime object to ISO format string for JSON serialization"""
    return dt.isoformat() if dt else None
