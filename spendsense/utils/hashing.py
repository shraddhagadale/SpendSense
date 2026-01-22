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


def compute_file_hash(file_path: str) -> str:
    """
    Compute SHA-256 hash of a file's contents.
    
    Args:
        file_path: Path to the file
    
    Returns:
        64-character hex string
    """
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()
