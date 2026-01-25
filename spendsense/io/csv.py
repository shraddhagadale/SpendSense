"""CSV file operations for transactions."""
import csv
from pathlib import Path

from spendsense.utils.dates import normalize_date


def load_transactions_csv(filename: str | Path) -> list[dict]:
    """
    Load transactions from a CSV file.

    Required columns: date, description, amount
    Optional columns: category, merchant
    
    Args:
        filename: Path to CSV file
    
    Returns:
        List of transaction dictionaries
    """
    transactions = []
    with open(filename, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            transactions.append({
                "date": normalize_date(row["date"]),
                "description": row["description"],
                "amount": float(row["amount"]),
                "category": row.get("category"),
                "merchant": row.get("merchant"),
            })
    return transactions


def write_transactions_csv(filename: str | Path, transactions: list[dict]) -> None:
    """
    Write transactions to a CSV file.
    
    Args:
        filename: Output path
        transactions: List of transaction dictionaries
    """
    fieldnames = ["date", "description", "amount", "category", "merchant"]
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(transactions)
