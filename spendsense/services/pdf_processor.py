"""
PDF Processing Service

This module handles extraction of transaction data from PDF files.
All PDFs are converted to images and processed with Tesseract OCR.

Flow:
1. Convert PDF pages to images
2. Extract text using Tesseract
3. Combine multi-line transactions
4. Parse transactions using regex patterns
5. Return structured transaction data
"""

import re
from pathlib import Path

from spendsense.services.ocr import extract_text_from_pdf


# Pattern: lines that START a transaction (dates like 11/01/25)
DATE_LINE = re.compile(
    r"""^\s*(
        \d{1,2}            # day or month
        [/\-]              # separator
        \d{1,2}
        (?:[/\-]\d{2,4})?  # optional year
    )\b""",
    re.VERBOSE,
)

# Pattern to extract date, description, amount from combined line
TXN_PATTERN = re.compile(
    r"^\s*(\d{2}/\d{2}/\d{2})\s+(.+?)\s+(-?\$?\d+\.\d{2})\s*$"
)


def read_pdf_lines(path: str) -> list[str]:
    """
    Extract text lines from a PDF file.
    
    Uses Tesseract OCR (via pdf2image) to treat all PDFs as images
    and extract text. This ensures consistent handling of both
    digital and scanned PDFs.
    
    Args:
        path: Path to the PDF file
        use_ocr: Ignored (kept for backward compatibility, OCR is always used)
        
    Returns:
        List of text lines extracted from the PDF
    """
    # Simply extract all text using Tesseract
    full_text = extract_text_from_pdf(path)
    all_lines = full_text.splitlines()

    # Filter to keep only the "New Charges Details" section
    filtered: list[str] = []
    in_details = False
    for line in all_lines:
        if "New Charges Details" in line:
            in_details = True
            continue
        if in_details and line.strip().startswith(("Fees", "Interest", "About ")):
            in_details = False
        if in_details:
            filtered.append(line)

    return filtered


def combine_wrapped_transactions(lines: list[str]) -> list[str]:
    """
    Combine 2-line transactions into one string.

    Example input lines:
        018: 11/01/25 ABC*NATIONAL INSTITUTE F  INDIANAPOLIS  IN
        019: 317-274-3432 $39.50
        
    Returns:
        ['11/01/25 ABC*NATIONAL INSTITUTE F INDIANAPOLIS IN 317-274-3432 $39.50', ...]
    """
    records: list[str] = []
    current: str | None = None

    for raw in lines:
        line = raw.strip()
        if not line:
            continue

        if DATE_LINE.match(line):
            # new transaction starts
            if current:
                records.append(current)
            current = line
        else:
            # continuation of previous transaction
            if current:
                current = current + " " + line

    if current:
        records.append(current)

    return records


def parse_transactions(records: list[str]) -> list[dict]:
    """
    Extract date, description, amount from combined transaction records.
    
    Args:
        records: List of combined transaction strings
        
    Returns:
        List of transaction dictionaries with keys: date, description, amount
    """
    txns: list[dict] = []

    for rec in records:
        m = TXN_PATTERN.match(rec)
        if not m:
            # Skip lines that don't match the pattern
            continue

        date, middle, amount = m.groups()

        # Normalize amount: drop $ sign
        amount = amount.replace("$", "")

        # Clean description
        description = middle.strip()

        txns.append(
            {
                "date": date,
                "description": description,
                "amount": amount,
            }
        )

    return txns


def process_pdf(
    pdf_path: str,
    use_ocr: bool = True,
    debug: bool = False
) -> list[dict]:
    """
    Complete PDF processing pipeline.
    
    This is the main function that orchestrates the entire process:
    1. Extract text from PDF (with OCR if needed)
    2. Combine multi-line transactions
    3. Parse transactions into structured data
    
    Args:
        pdf_path: Path to the PDF file
        use_ocr: Whether to use OCR for scanned PDFs
        debug: If True, print debug information
        
    Returns:
        List of transaction dictionaries
    """
    # Step 1: Extract lines from PDF
    lines = read_pdf_lines(pdf_path, use_ocr=use_ocr)
    
    # Step 2: Combine wrapped transactions
    records = combine_wrapped_transactions(lines)
    
    if debug:
        print("Combined records:")
        for r in records:
            print(">>>", r)
    
    # Step 3: Parse transactions
    transactions = parse_transactions(records)
    
    if debug:
        print(f"Parsed {len(transactions)} transactions")
        for t in transactions:
            print(t)
    
    return transactions
