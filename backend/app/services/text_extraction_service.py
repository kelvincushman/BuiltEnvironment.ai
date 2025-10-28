"""
Multi-OCR text extraction service for building documents.

Supports intelligent OCR backend selection:
- Dockling: Complex layouts, tables, building regulations
- DeepSeek-OCR: Technical drawings, blueprints, CAD documents
- Tesseract: Simple scans, fallback

Plus PyPDF2 for PDFs with text layers (always tried first).
"""

from pathlib import Path
from typing import Optional, Dict, Any, List
from enum import Enum
import logging

from ..core.config import settings

# PDF processing
try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False
    logging.warning("PyPDF2 not installed. PDF text extraction will be limited.")

# Tesseract OCR (fallback)
try:
    import pytesseract
    from PIL import Image
    HAS_TESSERACT = True
except ImportError:
    HAS_TESSERACT = False
    logging.warning("Tesseract not installed. Basic OCR will not be available.")

# Dockling (IBM document processing)
try:
    from docling.document_converter import DocumentConverter
    HAS_DOCKLING = True
except ImportError:
    HAS_DOCKLING = False
    logging.warning("Dockling not installed. Advanced document processing unavailable.")

# DeepSeek OCR
try:
    import requests
    HAS_DEEPSEEK = True
except ImportError:
    HAS_DEEPSEEK = False
    logging.warning("Requests not installed. DeepSeek-OCR unavailable.")

logger = logging.getLogger(__name__)


class DocumentCategory(str, Enum):
    """Document categories for OCR backend selection."""
    TECHNICAL_DRAWING = "technical_drawing"  # CAD, DWG, blueprints → DeepSeek-OCR
    COMPLEX_DOCUMENT = "complex_document"    # Regulations, specs, tables → Dockling
    SIMPLE_SCAN = "simple_scan"              # Simple scans → Tesseract
    TEXT_PDF = "text_pdf"                    # PDF with text layer → PyPDF2


class TextExtractionService:
    """
    Multi-backend text extraction service with intelligent OCR selection.

    Selection Strategy:
    1. Always try PyPDF2 first (PDFs with text layers)
    2. If scanned, detect document type:
       - Technical drawings → DeepSeek-OCR
       - Complex layouts → Dockling
       - Simple scans → Tesseract
    """

    def __init__(
        self,
        deepseek_url: Optional[str] = None,
        prefer_quality_over_speed: bool = True,
    ):
        """
        Initialize text extraction service.

        Args:
            deepseek_url: URL for DeepSeek-OCR service (from settings or override)
            prefer_quality_over_speed: If True, use higher quality OCR when available
        """
        self.deepseek_url = deepseek_url or settings.DEEPSEEK_OCR_URL
        self.prefer_quality = prefer_quality_over_speed

        # Technical drawing file extensions
        self.technical_extensions = {".dwg", ".dxf", ".ifc", ".rvt"}

    async def extract_from_file(
        self,
        file_path: Path,
        mime_type: str,
        document_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Extract text from a file using the best available method.

        Args:
            file_path: Path to file
            mime_type: MIME type of file
            document_type: Optional document type hint (e.g., "architectural", "structural")

        Returns:
            Dictionary with extracted data:
            {
                "text": str,
                "page_count": int,
                "method": str,  # "pypdf", "dockling", "deepseek", "tesseract", "unsupported"
                "metadata": dict,
                "confidence": float,  # OCR confidence if available
            }
        """
        # Determine document category
        category = self._categorize_document(file_path, mime_type, document_type)

        # Route to appropriate extraction method
        if mime_type == "application/pdf":
            # Try PyPDF2 first (fast and free for text-based PDFs)
            result = await self.extract_from_pdf(file_path)

            # If no text extracted, it's likely a scanned PDF
            if not result["text"].strip():
                logger.info(f"PDF has no text layer, using OCR (category: {category})")
                result = await self._extract_with_ocr(file_path, category, mime_type)

            return result

        elif mime_type.startswith("image/"):
            # Images always need OCR
            return await self._extract_with_ocr(file_path, category, mime_type)

        else:
            # Unsupported file type
            return {
                "text": "",
                "page_count": 0,
                "method": "unsupported",
                "metadata": {"mime_type": mime_type},
                "confidence": 0.0,
            }

    def _categorize_document(
        self,
        file_path: Path,
        mime_type: str,
        document_type: Optional[str],
    ) -> DocumentCategory:
        """
        Categorize document to select best OCR backend.

        Args:
            file_path: Path to file
            mime_type: MIME type
            document_type: Optional type hint

        Returns:
            DocumentCategory for OCR selection
        """
        # Check file extension for technical drawings
        if file_path.suffix.lower() in self.technical_extensions:
            return DocumentCategory.TECHNICAL_DRAWING

        # Check document type hints
        if document_type:
            doc_type_lower = document_type.lower()

            if any(
                keyword in doc_type_lower
                for keyword in ["drawing", "blueprint", "cad", "architectural", "structural"]
            ):
                return DocumentCategory.TECHNICAL_DRAWING

            if any(
                keyword in doc_type_lower
                for keyword in ["regulation", "specification", "code", "standard"]
            ):
                return DocumentCategory.COMPLEX_DOCUMENT

        # For images, check filename
        filename_lower = file_path.stem.lower()
        if any(
            keyword in filename_lower
            for keyword in ["drawing", "blueprint", "plan", "elevation", "section"]
        ):
            return DocumentCategory.TECHNICAL_DRAWING

        # Default to complex document (regulations, specs are common)
        if mime_type == "application/pdf":
            return DocumentCategory.COMPLEX_DOCUMENT

        # Simple scans for other images
        return DocumentCategory.SIMPLE_SCAN

    async def _extract_with_ocr(
        self,
        file_path: Path,
        category: DocumentCategory,
        mime_type: str,
    ) -> Dict[str, Any]:
        """
        Extract text using appropriate OCR backend based on category.

        Args:
            file_path: Path to file
            category: Document category
            mime_type: MIME type

        Returns:
            Extraction result dictionary
        """
        # Technical drawings → DeepSeek-OCR (best for technical content)
        if category == DocumentCategory.TECHNICAL_DRAWING:
            if HAS_DEEPSEEK:
                try:
                    return await self._extract_with_deepseek(file_path)
                except Exception as e:
                    logger.warning(f"DeepSeek-OCR failed: {e}, falling back to Dockling")

        # Complex documents → Dockling (best for layouts/tables)
        if category in [DocumentCategory.COMPLEX_DOCUMENT, DocumentCategory.TECHNICAL_DRAWING]:
            if HAS_DOCKLING:
                try:
                    return await self._extract_with_dockling(file_path)
                except Exception as e:
                    logger.warning(f"Dockling failed: {e}, falling back to Tesseract")

        # Fallback → Tesseract (simple, reliable)
        if HAS_TESSERACT:
            if mime_type == "application/pdf":
                return await self._extract_pdf_with_tesseract(file_path)
            else:
                return await self.extract_from_image(file_path)

        # No OCR available
        logger.error("No OCR backend available for extraction")
        return {
            "text": "",
            "page_count": 0,
            "method": "no_ocr_available",
            "metadata": {},
            "confidence": 0.0,
        }

    async def extract_from_pdf(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract text from PDF using PyPDF2 (text layer extraction).

        Args:
            file_path: Path to PDF file

        Returns:
            Extraction result
        """
        if not HAS_PYPDF2:
            return {
                "text": "",
                "page_count": 0,
                "method": "pypdf_unavailable",
                "metadata": {},
                "confidence": 0.0,
            }

        try:
            text_parts = []
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
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(f"\n\n--- Page {page_num + 1} ---\n\n")
                        text_parts.append(page_text)

            extracted_text = "".join(text_parts)

            return {
                "text": extracted_text,
                "page_count": page_count,
                "method": "pypdf",
                "metadata": metadata,
                "confidence": 1.0 if extracted_text.strip() else 0.0,
            }

        except Exception as e:
            logger.error(f"PyPDF2 extraction failed: {e}")
            return {
                "text": "",
                "page_count": 0,
                "method": "pypdf_error",
                "metadata": {"error": str(e)},
                "confidence": 0.0,
            }

    async def _extract_with_dockling(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract text using Dockling (IBM document processing).

        Best for: Complex layouts, tables, regulations, specifications.

        Args:
            file_path: Path to file

        Returns:
            Extraction result
        """
        try:
            converter = DocumentConverter()
            result = converter.convert(str(file_path))

            # Dockling returns structured document
            text = result.document.export_to_markdown()
            page_count = len(result.document.pages) if hasattr(result.document, "pages") else 1

            return {
                "text": text,
                "page_count": page_count,
                "method": "dockling",
                "metadata": {
                    "has_tables": True,  # Dockling preserves table structure
                    "layout_preserved": True,
                },
                "confidence": 0.95,  # Dockling is very accurate
            }

        except Exception as e:
            logger.error(f"Dockling extraction failed: {e}")
            raise

    async def _extract_with_deepseek(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract text using DeepSeek-OCR API.

        Best for: Technical drawings, blueprints, CAD documents, handwritten annotations.

        Args:
            file_path: Path to file

        Returns:
            Extraction result
        """
        try:
            # Convert to image if PDF
            if file_path.suffix.lower() == ".pdf":
                # For PDFs, convert first page to image for DeepSeek
                # (Or send PDF directly if DeepSeek supports it)
                image_path = await self._pdf_to_image(file_path)
            else:
                image_path = file_path

            # Call DeepSeek-OCR API
            with open(image_path, "rb") as f:
                files = {"file": (file_path.name, f, "image/png")}
                response = requests.post(
                    f"{self.deepseek_url}/ocr",
                    files=files,
                    timeout=60,
                )
                response.raise_for_status()

            result = response.json()

            return {
                "text": result.get("text", ""),
                "page_count": 1,  # DeepSeek processes per-page
                "method": "deepseek",
                "metadata": {
                    "confidence": result.get("confidence", 0.0),
                    "bboxes": result.get("bboxes", []),  # Bounding boxes for drawings
                },
                "confidence": result.get("confidence", 0.85),
            }

        except Exception as e:
            logger.error(f"DeepSeek-OCR extraction failed: {e}")
            raise

    async def _extract_pdf_with_tesseract(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract text from scanned PDF using Tesseract OCR.

        Args:
            file_path: Path to PDF file

        Returns:
            Extraction result
        """
        try:
            # Convert PDF pages to images and OCR each
            from pdf2image import convert_from_path

            images = convert_from_path(file_path)
            text_parts = []

            for i, image in enumerate(images):
                page_text = pytesseract.image_to_string(image)
                text_parts.append(f"\n\n--- Page {i + 1} ---\n\n")
                text_parts.append(page_text)

            return {
                "text": "".join(text_parts),
                "page_count": len(images),
                "method": "tesseract",
                "metadata": {},
                "confidence": 0.75,  # Tesseract is less accurate than Dockling/DeepSeek
            }

        except Exception as e:
            logger.error(f"Tesseract PDF extraction failed: {e}")
            return {
                "text": "",
                "page_count": 0,
                "method": "tesseract_error",
                "metadata": {"error": str(e)},
                "confidence": 0.0,
            }

    async def extract_from_image(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract text from image using Tesseract OCR.

        Args:
            file_path: Path to image file

        Returns:
            Extraction result
        """
        if not HAS_TESSERACT:
            return {
                "text": "",
                "page_count": 0,
                "method": "tesseract_unavailable",
                "metadata": {},
                "confidence": 0.0,
            }

        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)

            # Get image dimensions
            width, height = image.size

            return {
                "text": text,
                "page_count": 1,
                "method": "tesseract",
                "metadata": {
                    "image_width": width,
                    "image_height": height,
                    "image_format": image.format,
                },
                "confidence": 0.75,
            }

        except Exception as e:
            logger.error(f"Image extraction failed: {e}")
            return {
                "text": "",
                "page_count": 0,
                "method": "tesseract_error",
                "metadata": {"error": str(e)},
                "confidence": 0.0,
            }

    async def _pdf_to_image(self, pdf_path: Path) -> Path:
        """
        Convert first page of PDF to image for DeepSeek-OCR.

        Args:
            pdf_path: Path to PDF

        Returns:
            Path to generated image
        """
        from pdf2image import convert_from_path

        images = convert_from_path(pdf_path, first_page=1, last_page=1)
        image_path = pdf_path.parent / f"{pdf_path.stem}_page1.png"
        images[0].save(image_path, "PNG")
        return image_path


# Global text extraction service instance
text_extraction_service = TextExtractionService()
