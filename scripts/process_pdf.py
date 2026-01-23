#!/usr/bin/env python3
"""
PDF to CSV Processor Script

This script processes credit card statement PDFs and extracts transactions to CSV.

Usage:
    python scripts/process_pdf.py

What it does:
    1. Reads PDF from data/credit_card_statement-2.pdf
    2. Automatically detects if PDF is scanned or organic
    3. Uses OCR if needed (for scanned PDFs)
    4. Extracts transactions using pattern matching
    5. Writes results to data/credit_card_statements.csv
"""

import csv
from pathlib import Path

from spendsense.services.pdf_processor import process_pdf
from spendsense.services.ocr import is_ocr_available


def write_csv(transactions: list[dict], csv_path: str) -> None:
    """Write transactions to a CSV file."""
    fieldnames = ["date", "description", "amount"]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(transactions)


def main():
    """Main entry point for PDF processing."""
    # Configuration
    pdf_path = "data/credit_card_statement-2.pdf"
    csv_path = "data/credit_card_statements.csv"
    
    print("=" * 60)
    print("PDF to CSV Processor")
    print("=" * 60)
    
    # Check OCR availability
    if is_ocr_available():
        print("✅ OCR support: Available (will auto-detect scanned PDFs)")
    else:
        print("⚠️  OCR support: Not available")
        print("   Install with: pip install ocrmypdf && brew install tesseract")
    
    print(f"\nProcessing: {pdf_path}")
    
    # Process the PDF
    transactions = process_pdf(pdf_path, use_ocr=True, debug=False)
    
    # Write to CSV
    write_csv(transactions, csv_path)
    
    print(f"✅ Extracted {len(transactions)} transactions")
    print(f"✅ Wrote CSV to: {csv_path}")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
