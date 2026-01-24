#!/usr/bin/env python3
"""
Seamless PDF to Categorized CSV Pipeline
-----------------------------------------
This script combines PDF processing and transaction categorization into a single step.

Usage:
    python scripts/process_and_categorize.py <pdf_path> [--output <csv_path>]

Example:
    python scripts/process_and_categorize.py data/statement.pdf
    python scripts/process_and_categorize.py data/statement.pdf --output data/my_transactions.csv
"""

import argparse
import sys
import time
from pathlib import Path
from typing import Optional
from collections import Counter

# Import PDF processing service
from spendsense.services.pdf_processor import (
    read_pdf_lines,
    combine_wrapped_transactions,
    parse_transactions,
)

# Import LLM service for categorization
from spendsense.services.llm import LLMService
from spendsense.services.prompts import build_category_prompt
from spendsense.core.constants import CATEGORIES

# Import CSV utilities
from spendsense.io.csv import write_transactions_csv


def process_and_categorize_pdf(
    pdf_path: str,
    output_csv: Optional[str] = None,
    use_ocr: bool = True,
) -> str:
    """
    Complete pipeline: PDF → Extracted Transactions → Categorized CSV
    
    Args:
        pdf_path: Path to the PDF statement
        output_csv: Optional custom output path (defaults to <pdf_name>_categorized.csv)
        use_ocr: Whether to use OCR for scanned PDFs
    
    Returns:
        Path to the generated categorized CSV file
    """
    pdf_path_obj = Path(pdf_path)
    
    if not pdf_path_obj.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    print(f"📄 Processing PDF: {pdf_path_obj.name}")
    print("=" * 60)
    
    # Step 1: Extract text from PDF
    print("\n[1/4] 📖 Extracting text from PDF...")
    lines = read_pdf_lines(str(pdf_path_obj), use_ocr=use_ocr)
    print(f"Extracted {len(lines)} lines")
    
    # Step 2: Combine wrapped transactions
    print("\n[2/4] 🔗 Combining wrapped transactions...")
    combined_lines = combine_wrapped_transactions(lines)
    print(f"Combined into {len(combined_lines)} transaction lines")
    
    # Step 3: Parse transactions
    print("\n[3/4] 🔍 Parsing transaction details...")
    transactions = parse_transactions(combined_lines)
    print(f"Parsed {len(transactions)} transactions")
    
    if not transactions:
        print("\nNo transactions found in PDF!")
        sys.exit(1)
    
    # Step 4: Categorize transactions using LLM
    print("\n[4/4] 🤖 Categorizing transactions with AI...")
    llm = LLMService()
    
    try:
        categorized = []
        total = len(transactions)
        idx_width = len(str(total))
        
        for i, transaction in enumerate(transactions, start=1):
            description = transaction["description"]
            amount = float(transaction["amount"])  # Convert string to float
            
            # Build categorization prompt
            prompt = build_category_prompt(description, amount, CATEGORIES)
            category = llm.ask(prompt)
            
            # Add category to transaction
            transaction["category"] = category
            categorized.append(transaction)
            
            # Show progress
            short_desc = (description[:50] + "…") if len(description) > 50 else description
            print(f"      [{i:>{idx_width}}/{total}] {category:<16} ${amount:>8.2f}  {short_desc}")
            
            # Rate limiting to avoid API throttling
            if i < total:
                time.sleep(0.5)
        
        transactions = categorized
        print(f"\n      ✓ Categorized {len(transactions)} transactions")
        
    except Exception as e:
        print(f"\n⚠️  Categorization failed: {e}")
        print("      Proceeding without categories...")
        # Add empty category field
        for transaction in transactions:
            transaction["category"] = ""
    
    # Step 5: Write to CSV
    if output_csv is None:
        output_csv = str(pdf_path_obj.parent / f"{pdf_path_obj.stem}_categorized.csv")
    
    output_path = Path(output_csv)
    write_transactions_csv(str(output_path), transactions)
    
    print("\n" + "=" * 60)
    print(f"✅ Success! Categorized transactions saved to:")
    print(f"   {output_path.absolute()}")
    print(f"\n📊 Summary:")
    print(f"   • Total transactions: {len(transactions)}")
    
    # Show category breakdown if categorization succeeded
    if transactions and transactions[0].get("category"):
        category_counts = Counter(t.get("category", "Unknown") for t in transactions)
        
        print(f"   • Categories found: {len(category_counts)}")
        print(f"\n   Category breakdown:")
        for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"     - {cat:<20} {count:>3} transactions")
    
    print("=" * 60)
    
    return str(output_path)


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Process PDF statement and categorize transactions in one step",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a PDF with auto-generated output filename
  python scripts/process_and_categorize.py --input data/statement.pdf
  
  # Process with custom output path
  python scripts/process_and_categorize.py --input data/statement.pdf --output data/my_transactions.csv
  
  # Skip OCR (for text-based PDFs only)
  python scripts/process_and_categorize.py --input data/statement.pdf --no-ocr
        """,
    )
    
    parser.add_argument(
        "-i", "--input",
        required=True,
        help="Path to the PDF credit card statement",
        dest="pdf_path",
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Output CSV file path (default: <pdf_name>_categorized.csv)",
        default=None,
    )
    
    parser.add_argument(
        "--no-ocr",
        action="store_true",
        help="Disable OCR processing (only use for text-based PDFs)",
    )
    
    args = parser.parse_args()
    
    try:
        process_and_categorize_pdf(
            pdf_path=args.pdf_path,
            output_csv=args.output,
            use_ocr=not args.no_ocr,
        )
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
