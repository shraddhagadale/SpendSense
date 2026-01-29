#!/usr/bin/env python3
"""
Analytics Script

This script provides analytics on categorized transactions.

Usage:
    python scripts/analytics.py

What it does:
    1. Imports categorized transactions to database
    2. Shows available months
    3. Lets you select a month to analyze
    4. Shows spending breakdown by category
    5. Shows top transactions for the month
"""

import psycopg2
from datetime import datetime, UTC
from pathlib import Path

from spendsense.config.settings import settings
from spendsense.io.csv import load_transactions_csv
from spendsense.utils.hashing import compute_dedupe_hash
from spendsense.utils.dates import normalize_date


def get_db_connection():
    """Get a database connection to PostgreSQL."""
    return psycopg2.connect(settings.database_url)


def import_to_db(csv_path: str):
    """Import categorized transactions to database with new schema.
    
    Args:
        csv_path: Path to the categorized CSV file
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Load transactions from CSV
    transactions = load_transactions_csv(csv_path)

    
    # Transform and insert each transaction
    for txn in transactions:
        posted_date = normalize_date(txn["date"])
        amount = float(txn["amount"])
        description = txn["description"]
        category = txn.get("category", "")
        merchant_clean = txn.get("merchant", "Unknown")
        dedupe_hash = compute_dedupe_hash(posted_date, amount, description)
        
        cursor.execute("""
            INSERT INTO transactions (posted_date, amount, description, merchant_clean, category, statement_id, dedupe_hash)
            VALUES (%s, %s, %s, %s, %s, NULL, %s)
            ON CONFLICT (dedupe_hash) DO NOTHING
        """, (posted_date, amount, description, merchant_clean, category, dedupe_hash))
    
    conn.commit()
    conn.close()


def get_category_totals(conn):
    """Get total spending by category."""
    cursor = conn.cursor()
    cursor.execute("""
    SELECT category, SUM(amount) AS total
                   FROM transactions
                   GROUP BY category
    """) 
    rows = cursor.fetchall()
    return rows


def get_months(conn):
    """Get available months in the transactions table."""
    cursor = conn.cursor()
    cursor.execute("""
                    SELECT DISTINCT to_char(posted_date, 'YYYY-MM') AS month
                    FROM transactions
                    ORDER BY month
                   """)
    return [row[0] for row in cursor.fetchall()]


def get_monthly_totals(conn):
    """Get monthly total expenses."""
    cursor = conn.cursor()
    cursor.execute("""
                    SELECT to_char(posted_date, 'YYYY-MM') AS month, SUM(amount) AS total
                    FROM transactions
                   GROUP BY month
                   ORDER BY month
                   """)
    return [(row[0],row[1]) for row in cursor.fetchall()]


def get_transactions_for_month(conn, month):
    """Get all transactions for a given month."""
    cursor = conn.cursor()
    cursor.execute("""
                    SELECT posted_date, description, amount, category
                    FROM transactions
                    WHERE to_char(posted_date, 'YYYY-MM') = %s
                    ORDER BY posted_date
                   """, (month,))
    return [(row[0],row[1],row[2],row[3]) for row in cursor.fetchall()]

def get_category_totals_for_month(conn, month):
    """Get category totals for a specific month."""
    cursor = conn.cursor()
    cursor.execute("""
                    SELECT category, SUM(amount) AS total
                    FROM transactions
                    WHERE to_char(posted_date, 'YYYY-MM') = %s
                    GROUP BY category
                    ORDER BY total DESC
                   """, (month,))
    return [(row[0],row[1]) for row in cursor.fetchall()]


def get_biggest_transactions(conn, month, limit=5):
    """Get top biggest transactions for the month."""
    cursor = conn.cursor()
    cursor.execute("""
                    SELECT posted_date, merchant_clean, amount, category
                    FROM transactions
                    WHERE to_char(posted_date, 'YYYY-MM') = %s
                    ORDER BY ABS(amount) DESC
                    LIMIT %s
                   """, (month, limit))
    return cursor.fetchall()


def run_analytics(csv_path: str) -> bool:
    """
    Run analytics on a categorized CSV file.
    
    This function can be called programmatically by other scripts.
    
    Args:
        csv_path: Path to the categorized CSV file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        print("=" * 60)
        print("Transaction Analytics")
        print("=" * 60)
        
        # Import data
        print("\nImporting transactions to database...")
        import_to_db(csv_path)
        conn = get_db_connection()
        
        # Print available months
        months = get_months(conn)
        if not months:
            print(" No data found in DB.")
            conn.close()
            return False

        print("\nAvailable months:")
        for idx, m in enumerate(months, start=1):
            print(f"  {idx}. {m}")

        choice = input("\nSelect a month by number (default latest): ").strip()

        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(months):
                current_month = months[idx - 1]
            else:
                current_month = months[-1]
        else:
            current_month = months[-1]

        print(f"\nAnalyzing month: {current_month}")
        print("=" * 60)

        # Total spent in the selected month
        month_txns = get_transactions_for_month(conn, current_month)
        selected_total = sum(txn[2] for txn in month_txns)
        print(f"\n💰 Total spent: ${selected_total:.2f}")
        print(f"📝 Transactions: {len(month_txns)}")

        # Category totals for the selected month
        cat_totals = get_category_totals_for_month(conn, current_month)
        print("\n📂 Category breakdown:")
        if cat_totals:
            name_width = max(len(str(c[0] or "")) for c in cat_totals)
            for category, total in cat_totals:
                pct = (total / selected_total * 100) if selected_total else 0
                print(f"  - {category:<{name_width}}  ${total:>10.2f}  ({pct:>5.1f}%)")
        else:
            print("  - (no categories found)")

        # Biggest transactions for the selected month
        top_txns = get_biggest_transactions(conn, current_month, limit=5)
        print("\n🔝 Top 5 transactions:")
        for date, merchant, amount, category in top_txns:
            merchant_str = str(merchant) if merchant else "Unknown"
            merchant_display = merchant_str[:50] if len(merchant_str) > 50 else merchant_str
            print(f"  {date} | {category:<15} | {merchant_display:<25} | ${amount:>8.2f}")
        
        print("\n" + "=" * 60)
        conn.close()
        return True
        
    except Exception as e:
        print(f"\nAnalytics failed: {e}")
        return False



