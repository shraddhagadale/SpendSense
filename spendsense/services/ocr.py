"""
OCR service using Tesseract and pdf2image.

This module extracts text from ANY PDF (scanned or digital) by:
1. Converting PDF pages to high-res images (using pdf2image)
2. Running Tesseract OCR on each image (using pytesseract)

This ensures consistent behavior regardless of how the PDF was created.
"""

from typing import List
try:
    import pytesseract
    from pdf2image import convert_from_path
except ImportError:
    pytesseract = None
    convert_from_path = None


def is_ocr_available() -> bool:
    """Check if necessary OCR libraries are installed."""
    return pytesseract is not None and convert_from_path is not None


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from a PDF file using Tesseract OCR.
    
    Converts PDF pages to images and runs OCR on them.
    This works for both scanned and natively digital PDFs.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        The complete extracted text as a single string.
        
    Raises:
        RuntimeError: If libraries are missing or OCR fails
    """
    if not is_ocr_available():
        raise RuntimeError(
            "Missing OCR dependencies.\n"
            "Please install: pip install pytesseract pdf2image pillow\n"
            "And ensure Tesseract and Poppler are installed on your system."
        )

    try:
        # Convert PDF to list of images (one per page)
        # default dpi=200 is a good trade-off for speed/accuracy; 300 is slower/better
        images = convert_from_path(pdf_path, dpi=300)
        
        full_text = []
        for i, image in enumerate(images):
            # Run Tesseract on the image
            text = pytesseract.image_to_string(image)
            full_text.append(text)
            
        return "\n".join(full_text)
        
    except Exception as e:
        raise RuntimeError(f"OCR failed: {e}") from e
