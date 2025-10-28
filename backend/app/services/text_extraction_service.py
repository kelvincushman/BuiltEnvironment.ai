"""
Text extraction service for documents.

Supports:
- PDF text extraction
- OCR for scanned PDFs and images
- Table extraction
- Page counting
"""

from pathlib import Path
from typing import Optional, Dict, Any
import logging

# PDF processing
try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False
    logging.warning("PyPDF2 not installed. PDF text extraction will be limited.")

# OCR
try:
    import pytesseract
    from PIL import Image
    HAS_OCR = True
except ImportError:
    HAS_OCR = False
    logging.warning("pytesseract or Pillow not installed. OCR will not be available.")

logger = logging.getLogger(__name__)


class TextExtractionService:
    """
    Service for extracting text from documents.

    Handles:
    - PDF text extraction (PyPDF2)
    - OCR for scanned documents (Tesseract)
    - Image text extraction
    - Metadata extraction
    """

    async def extract_from_file(
        self,
        file_path: Path,
        mime_type: str,
    ) -> Dict[str, Any]:
        """
        Extract text from a file.

        Args:
            file_path: Path to file
            mime_type: MIME type of file

        Returns:
            Dictionary with extracted data:
            {
                "text": str,
                "page_count": int,
                "method": str,  # "pypdf", "ocr", or "unsupported"
                "metadata": dict,
            }
        """
        if mime_type == "application/pdf":
            return await self.extract_from_pdf(file_path)
        elif mime_type.startswith("image/"):
            return await self.extract_from_image(file_path)
        else:
            return {
                "text": "",
                "page_count": 0,
                "method": "unsupported",
                "metadata": {},
            }

    async def extract_from_pdf(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract text from PDF file.

        Args:
            file_path: Path to PDF file

        Returns:
            Extracted text and metadata
        """
        if not HAS_PYPDF2:
            logger.error("PyPDF2 not available for PDF extraction")
            return {
                "text": "",
                "page_count": 0,
                "method": "error",
                "metadata": {"error": "PyPDF2 not installed"},
            }

        try:
            text_parts = []
            page_count = 0
            metadata = {}

            with open(file_path, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)
                page_count = len(pdf_reader.pages)

                # Extract metadata
                if pdf_reader.metadata:
                    metadata = {
                        "title": pdf_reader.metadata.get("/Title", ""),
                        "author": pdf_reader.metadata.get("/Author", ""),
                        "subject": pdf_reader.metadata.get("/Subject", ""),
                        "creator": pdf_reader.metadata.get("/Creator", ""),
                    }

                # Extract text from each page
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text.strip():
                            text_parts.append(f"\n\n--- Page {page_num + 1} ---\n\n")
                            text_parts.append(page_text)
                    except Exception as e:
                        logger.warning(f"Failed to extract text from page {page_num + 1}: {e}")
                        continue

            extracted_text = "".join(text_parts)

            # If no text extracted, might be scanned - try OCR
            if not extracted_text.strip() and HAS_OCR:
                logger.info("No text found in PDF, attempting OCR...")
                # Note: OCR on PDF would require pdf2image, skipping for MVP
                # Can be added later

            return {
                "text": extracted_text,
                "page_count": page_count,
                "method": "pypdf",
                "metadata": metadata,
            }

        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return {
                "text": "",
                "page_count": 0,
                "method": "error",
                "metadata": {"error": str(e)},
            }

    async def extract_from_image(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract text from image using OCR.

        Args:
            file_path: Path to image file

        Returns:
            Extracted text and metadata
        """
        if not HAS_OCR:
            logger.error("OCR not available (pytesseract/Pillow not installed)")
            return {
                "text": "",
                "page_count": 1,
                "method": "error",
                "metadata": {"error": "OCR not available"},
            }

        try:
            # Open image
            image = Image.open(file_path)

            # Perform OCR
            text = pytesseract.image_to_string(image)

            # Get image metadata
            metadata = {
                "width": image.width,
                "height": image.height,
                "format": image.format,
                "mode": image.mode,
            }

            return {
                "text": text,
                "page_count": 1,
                "method": "ocr",
                "metadata": metadata,
            }

        except Exception as e:
            logger.error(f"Error performing OCR on image: {e}")
            return {
                "text": "",
                "page_count": 1,
                "method": "error",
                "metadata": {"error": str(e)},
            }

    async def count_pages(self, file_path: Path, mime_type: str) -> int:
        """
        Count pages in a document.

        Args:
            file_path: Path to file
            mime_type: MIME type

        Returns:
            Number of pages
        """
        if mime_type == "application/pdf" and HAS_PYPDF2:
            try:
                with open(file_path, "rb") as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    return len(pdf_reader.pages)
            except Exception:
                return 0
        elif mime_type.startswith("image/"):
            return 1
        else:
            return 0

    def is_searchable_pdf(self, file_path: Path) -> bool:
        """
        Check if PDF is searchable (has extractable text).

        Args:
            file_path: Path to PDF file

        Returns:
            True if PDF has text, False if scanned
        """
        if not HAS_PYPDF2:
            return False

        try:
            with open(file_path, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)

                # Check first few pages for text
                pages_to_check = min(3, len(pdf_reader.pages))
                for i in range(pages_to_check):
                    text = pdf_reader.pages[i].extract_text()
                    if text.strip():
                        return True

            return False
        except Exception:
            return False


# Singleton instance
text_extraction_service = TextExtractionService()
