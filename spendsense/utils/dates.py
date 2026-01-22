"""Date parsing and normalization utilities."""
from __future__ import annotations

from datetime import datetime


def normalize_date(date_str: str) -> str:
    """
    Normalize common transaction date formats to ISO: YYYY-MM-DD.

    Supports:
    - YYYY-MM-DD
    - MM/DD/YY
    - MM/DD/YYYY
    - MM-DD-YY
    - MM-DD-YYYY
    
    Args:
        date_str: Date string in various formats
    
    Returns:
        ISO formatted date string (YYYY-MM-DD)
    """
    s = (date_str or "").strip()
    if not s:
        return s

    formats = ("%Y-%m-%d", "%m/%d/%y", "%m/%d/%Y", "%m-%d-%y", "%m-%d-%Y")
    for fmt in formats:
        try:
            return datetime.strptime(s, fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass

    # Return as-is if format not recognized
    return s


def parse_date(date_str: str) -> datetime | None:
    """
    Parse a date string into a datetime object.
    
    Args:
        date_str: Date string in various formats
    
    Returns:
        datetime object or None if parsing fails
    """
    s = (date_str or "").strip()
    if not s:
        return None

    formats = ("%Y-%m-%d", "%m/%d/%y", "%m/%d/%Y", "%m-%d-%y", "%m-%d-%Y")
    for fmt in formats:
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass

    return None
