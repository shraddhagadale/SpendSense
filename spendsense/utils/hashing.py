"""Hashing utilities for deduplication."""
import hashlib
from datetime import date


def compute_dedupe_hash(posted_date: date | str, amount: float, description: str) -> str:
    """
    Compute SHA-256 hash for transaction deduplication.
    
    Args:
        posted_date: Transaction date (date object or YYYY-MM-DD string)
        amount: Transaction amount
        description: Raw description text
    
    Returns:
        64-character hex string
    """
    date_str = posted_date.isoformat() if isinstance(posted_date, date) else str(posted_date)
    amount_str = f"{abs(amount):.2f}"
    desc_str = description.lower().strip()
    
    raw = f"{date_str}|{amount_str}|{desc_str}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

