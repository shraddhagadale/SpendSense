"""
OCR service for processing scanned PDFs.

This module handles OCR (Optical Character Recognition) for PDFs that don't
have extractable text. It uses ocrmypdf which internally uses Tesseract OCR.

How it works:
1. For text-based PDFs: PyPDF2 can extract text directly (no OCR needed)
2. For scanned PDFs: ocrmypdf adds a searchable text layer, then PyPDF2 can extract

The service intelligently detects if OCR is needed by checking if text extraction
returns very little text (indicating a scanned image).
"""

import tempfile
from pathlib import Path
from typing import Optional

try:
    import ocrmypdf
except ImportError:
    ocrmypdf = None  # Graceful degradation if not installed


def is_ocr_available() -> bool:
    """Check if ocrmypdf is installed and available."""
    return ocrmypdf is not None


def needs_ocr(pdf_path: str, min_text_threshold: int = 100) -> bool:
    """
    Check if a PDF needs OCR processing.
    
    Args:
        pdf_path: Path to the PDF file
        min_text_threshold: Minimum number of characters to consider PDF as text-based
        
    Returns:
        True if PDF appears to be scanned (needs OCR), False otherwise
    """
    from PyPDF2 import PdfReader
    
    try:
        reader = PdfReader(pdf_path)
        total_text = ""
        for page in reader.pages:
            text = page.extract_text() or ""
            total_text += text
        
        # If we extracted very little text, it's likely a scanned PDF
        return len(total_text.strip()) < min_text_threshold
    except Exception:
        # If extraction fails, assume OCR is needed
        return True


def process_pdf_with_ocr(
    input_path: str,
    output_path: Optional[str] = None,
    force_ocr: bool = False,
) -> str:
    """
    Process a PDF with OCR if needed.
    
    This function:
    1. Checks if OCR is needed (unless force_ocr=True)
    2. If needed, runs ocrmypdf to add a searchable text layer
    3. Returns the path to the processed PDF (original or OCR'd version)
    
    Args:
        input_path: Path to input PDF file
        output_path: Optional path for OCR'd output. If None, uses temp file
        force_ocr: If True, always run OCR even if text extraction works
        
    Returns:
        Path to the processed PDF (ready for text extraction)
        
    Raises:
        RuntimeError: If ocrmypdf is not installed
        Exception: If OCR processing fails
    """
    if not is_ocr_available():
        raise RuntimeError(
            "ocrmypdf is not installed. Install it with: pip install ocrmypdf\n"
            "Note: ocrmypdf requires Tesseract OCR. Install it:\n"
            "  - macOS: brew install tesseract\n"
            "  - Ubuntu/Debian: sudo apt-get install tesseract-ocr\n"
            "  - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki"
        )
    
    # Check if OCR is needed
    if not force_ocr and not needs_ocr(input_path):
        # PDF already has extractable text, return original
        return input_path
    
    # Determine output path
    if output_path is None:
        # Create a temporary file for the OCR'd PDF
        temp_dir = Path(input_path).parent
        temp_file = tempfile.NamedTemporaryFile(
            suffix=".pdf",
            dir=temp_dir,
            delete=False
        )
        output_path = temp_file.name
        temp_file.close()
    
    # Run OCR
    # ocrmypdf adds a searchable text layer to the PDF
    # This makes scanned PDFs readable by PyPDF2
    try:
        ocrmypdf.ocr(
            input_file=input_path,
            output_file=output_path,
            skip_text=True,  # Skip if text layer already exists (optimization)
            language="eng",  # English language for OCR
            optimize=1,  # Light optimization (0=none, 1=light, 2=aggressive)
        )
        return output_path
    except Exception as e:
        # Clean up temp file if we created it
        if output_path != input_path:
            try:
                Path(output_path).unlink()
            except Exception:
                pass
        raise RuntimeError(f"OCR processing failed: {e}") from e
