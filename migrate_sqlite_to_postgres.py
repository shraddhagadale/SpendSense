"""
One-time migration script: SQLite → PostgreSQL

Usage:
    1. Make sure PostgreSQL is running and the database exists
    2. Set environment variables:
       - DB_TYPE=postgres
       - PG_HOST, PG_PORT, PG_USER, PG_PASSWORD, PG_DATABASE (or DATABASE_URL)
    3. Run Alembic migrations first:  alembic upgrade head
    4. Run this script:  python migrate_sqlite_to_postgres.py

This script:
    - Reads all transactions from the local SQLite database (old schema)
    - Transforms data to new schema (adding dedupe_hash, etc.)
    - Inserts them into PostgreSQL in batches
    - Reports progress and any errors
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError

from config import get_database_url, SQLITE_PATH, DB_TYPE
from spendsense.utils import compute_dedupe_hash, clean_merchant_name

BATCH_SIZE = 100


def get_sqlite_transactions():
    """Read all transactions from old SQLite schema."""
    if not SQLITE_PATH.exists():
        print(f"SQLite database not found at {SQLITE_PATH}")
        return []

    conn = sqlite3.connect(SQLITE_PATH)
    cursor = conn.cursor()

    # Check if old schema exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transactions'")
    if not cursor.fetchone():
        print("No transactions table found in SQLite.")
        conn.close()
        return []

    # Read from old schema: date, description, amount, category, imported_at
    cursor.execute("""
        SELECT date, description, amount, category, imported_at
        FROM transactions
        ORDER BY date
    """)

    rows = cursor.fetchall()
    conn.close()

    transactions = []
    for row in rows:
        date_str, description, amount, category, imported_at = row
        
        # Parse date (could be YYYY-MM-DD or MM/DD/YY)
        try:
            if "/" in date_str:
                posted_date = datetime.strptime(date_str, "%m/%d/%y").date()
            else:
                posted_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            posted_date = datetime.now().date()
        
        # Compute dedupe hash
        dedupe_hash = compute_dedupe_hash(posted_date, amount, description)
        
        # Clean merchant name
        merchant_clean = clean_merchant_name(description)
        
        transactions.append({
            "posted_date": posted_date,
            "amount": abs(amount),  # Store positive
            "description": description,
            "merchant_clean": merchant_clean,
            "category": category,
            "statement_id": None,  # Old data has no statement reference
            "dedupe_hash": dedupe_hash,
        })

    return transactions


def insert_to_postgres(transactions: list[dict]):
    """Insert transactions into PostgreSQL in batches."""
    if DB_TYPE != "postgres":
        print("ERROR: DB_TYPE must be 'postgres' to run this migration.")
        print("Set environment variable: export DB_TYPE=postgres")
        return False

    engine = create_engine(get_database_url())

    inserted = 0
    skipped = 0
    errors = 0

    print(f"Migrating {len(transactions)} transactions to PostgreSQL...")
    db_info = get_database_url().split('@')[-1] if '@' in get_database_url() else '(local)'
    print(f"Connection: {db_info}")

    with engine.connect() as conn:
        for i in range(0, len(transactions), BATCH_SIZE):
            batch = transactions[i : i + BATCH_SIZE]

            for txn in batch:
                try:
                    conn.execute(
                        text("""
                            INSERT INTO transactions 
                                (posted_date, amount, description, merchant_clean, category, statement_id, dedupe_hash)
                            VALUES 
                                (:posted_date, :amount, :description, :merchant_clean, :category, :statement_id, :dedupe_hash)
                            ON CONFLICT (dedupe_hash) DO NOTHING
                        """),
                        txn,
                    )
                    inserted += 1
                except IntegrityError:
                    skipped += 1
                except Exception as e:
                    errors += 1
                    print(f"  Error inserting transaction: {e}")

            conn.commit()
            processed = min(i + BATCH_SIZE, len(transactions))
            print(f"  Batch {i // BATCH_SIZE + 1}: {processed}/{len(transactions)} processed")

    print(f"\nMigration complete!")
    print(f"  Inserted: {inserted}")
    print(f"  Skipped (duplicates): {skipped}")
    print(f"  Errors: {errors}")

    return errors == 0


def main():
    print("=" * 50)
    print("SQLite → PostgreSQL Migration")
    print("=" * 50)
    print(f"Old schema: date, description, amount, category")
    print(f"New schema: posted_date, amount, description, merchant_clean, category, statement_id, dedupe_hash")
    print()

    # Read from SQLite
    transactions = get_sqlite_transactions()
    if not transactions:
        print("No transactions found in SQLite. Nothing to migrate.")
        return

    print(f"Found {len(transactions)} transactions in SQLite.\n")

    # Show sample transformation
    if transactions:
        sample = transactions[0]
        print("Sample transformation:")
        print(f"  posted_date:    {sample['posted_date']}")
        print(f"  amount:         {sample['amount']}")
        print(f"  description:    {sample['description'][:50]}...")
        print(f"  merchant_clean: {sample['merchant_clean']}")
        print(f"  category:       {sample['category']}")
        print(f"  dedupe_hash:    {sample['dedupe_hash'][:16]}...")
        print()

    # Insert into Postgres
    success = insert_to_postgres(transactions)

    if success:
        print("\n✓ Migration successful!")
        print("You can now switch your app to use PostgreSQL by setting DB_TYPE=postgres")
    else:
        print("\n✗ Migration completed with errors. Check the output above.")


if __name__ == "__main__":
    main()
