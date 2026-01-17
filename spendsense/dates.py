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
    """
    s = (date_str or "").strip()
    if not s:
        return s

    for fmt in ("%Y-%m-%d", "%m/%d/%y", "%m/%d/%Y", "%m-%d-%y", "%m-%d-%Y"):
        try:
            return datetime.strptime(s, fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass

    # If we don't recognize it, return as-is (better than crashing in v1).
    return s

