"""External services."""
from spendsense.services.llm import LLMService
from spendsense.services.prompts import build_category_prompt
from spendsense.services.ocr import (
    is_ocr_available,
    needs_ocr,
    process_pdf_with_ocr,
)

__all__ = [
    "LLMService",
    "build_category_prompt",
    "is_ocr_available",
    "needs_ocr",
    "process_pdf_with_ocr",
]
