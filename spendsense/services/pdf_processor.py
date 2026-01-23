"""
PDF Processing Service

This module handles extraction of transaction data from PDF files.
Supports both organic (text-based) and scanned (image-based) PDFs.

Flow:
1. Read PDF and extract text (with OCR if needed)
2. Combine multi-line transactions
3. Parse transactions using regex patterns
4. Return structured transaction data
"""

import re
from pathlib import Path
from PyPDF2 import PdfReader

from spendsense.services.ocr import is_ocr_available, process_pdf_with_ocr


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


def read_pdf_lines(path: str, use_ocr: bool = True) -> list[str]:
    """
    Extract text lines from a PDF file.
    
    This function intelligently handles both text-based and scanned PDFs:
    - For text-based PDFs: Extracts text directly (fast)
    - For scanned PDFs: Uses OCR to add a searchable text layer first
    
    Args:
        path: Path to the PDF file
        use_ocr: If True, automatically use OCR for scanned PDFs
        
    Returns:
        List of text lines extracted from the PDF
    """
    pdf_path = Path(path)
    processed_path = path  # Will be updated if OCR is needed
    
    # Step 1: Try OCR if enabled and available
    if use_ocr and is_ocr_available():
        try:
            # process_pdf_with_ocr checks if OCR is needed automatically
            # It returns the original path if text extraction works,
            # or a processed (OCR'd) path if scanning was detected
            processed_path = process_pdf_with_ocr(path)
        except Exception as e:
            # If OCR fails, fall back to direct extraction
            print(f"Warning: OCR processing failed ({e}), attempting direct extraction...")
            processed_path = path
    
    # Step 2: Extract text from PDF (original or OCR'd version)
    reader = PdfReader(processed_path)
    all_lines: list[str] = []

    for page in reader.pages:
        text = page.extract_text() or ""
        all_lines.extend(text.splitlines())

    # Step 3: Clean up temporary OCR file if one was created
    if processed_path != path and Path(processed_path).exists():
        try:
            Path(processed_path).unlink()
        except Exception:
            pass  # Ignore cleanup errors

    # Step 4: Filter to keep only the "New Charges Details" section
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
