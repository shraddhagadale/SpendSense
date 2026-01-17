import csv

from spendsense.dates import normalize_date


def load_transactions_csv(filename: str):
    """
    Load transactions from a CSV.

    Required columns: date, description, amount
    Optional column: category
    """
    transactions = []
    with open(filename, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            transactions.append(
                {
                    "date": normalize_date(row["date"]),
                    "description": row["description"],
                    "amount": float(row["amount"]),
                    "category": row.get("category"),
                }
            )
    return transactions


def write_transactions_csv(filename: str, transactions):
    """Write transactions to CSV with columns: date, description, amount, category."""
    fieldnames = ["date", "description", "amount", "category"]
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(transactions)

