#!/usr/bin/env python3
"""
OCR Functionality Tests

This module tests the OCR service to ensure it works correctly
with both organic (text-based) and scanned (image-based) PDFs.
"""

from pathlib import Path
import subprocess

from spendsense.services.ocr import is_ocr_available, needs_ocr, process_pdf_with_ocr


def test_ocr_setup():
    """Test if OCR is properly installed and configured."""
    print("=" * 60)
    print("OCR Setup Test")
    print("=" * 60)
    
    # Check if ocrmypdf is available
    if is_ocr_available():
        print("✅ ocrmypdf is installed and available")
    else:
        print("❌ ocrmypdf is NOT available")
        print("   Install with: pip install ocrmypdf")
        return False
    
    # Check if Tesseract is installed
    try:
        result = subprocess.run(
            ["tesseract", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✅ Tesseract is installed: {version_line}")
        else:
            print("❌ Tesseract command failed")
            return False
    except FileNotFoundError:
        print("❌ Tesseract is NOT installed")
        print("   Install with: brew install tesseract")
        return False
    except Exception as e:
        print(f"❌ Error checking Tesseract: {e}")
        return False
    
    print("\n✅ OCR setup is complete and ready to use!")
    return True


def test_pdf_detection():
    """Test PDF type detection (organic vs scanned)."""
    print("\n" + "=" * 60)
    print("PDF Detection Test")
    print("=" * 60)
    
    data_dir = Path("data")
    if not data_dir.exists():
        print("❌ data/ directory not found")
        return
    
    # Find all PDFs in data directory
    pdf_files = list(data_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("❌ No PDF files found in data/ directory")
        return
    
    print(f"\nFound {len(pdf_files)} PDF file(s):\n")
    
    for pdf_path in pdf_files:
        print(f"📄 {pdf_path.name}")
        
        try:
            is_scanned = needs_ocr(str(pdf_path))
            
            if is_scanned:
                print(f"   Type: 🖼️  SCANNED (needs OCR)")
            else:
                print(f"   Type: 📝 ORGANIC (text-based)")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()


def test_ocr_processing():
    """Test OCR processing on a sample PDF."""
    print("\n" + "=" * 60)
    print("OCR Processing Test")
    print("=" * 60)
    
    data_dir = Path("data")
    pdf_files = list(data_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("❌ No PDF files to test")
        return
    
    # Test with the first PDF
    test_pdf = pdf_files[0]
    print(f"\nTesting with: {test_pdf.name}")
    
    try:
        # Check if it needs OCR
        is_scanned = needs_ocr(str(test_pdf))
        print(f"Needs OCR: {is_scanned}")
        
        # Process the PDF
        print("\nProcessing PDF...")
        processed_path = process_pdf_with_ocr(str(test_pdf))
        
        if processed_path == str(test_pdf):
            print("✅ PDF already has text (no OCR needed)")
        else:
            print(f"✅ OCR completed successfully")
            print(f"   Processed file: {processed_path}")
            
            # Clean up temp file
            if Path(processed_path).exists():
                Path(processed_path).unlink()
                print("   Cleaned up temporary file")
        
    except Exception as e:
        print(f"❌ OCR processing failed: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run all OCR tests."""
    if test_ocr_setup():
        test_pdf_detection()
        test_ocr_processing()
    else:
        print("\n❌ OCR setup incomplete. Please install missing dependencies.")


if __name__ == "__main__":
    main()
