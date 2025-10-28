"""
Storage service for managing document files.

Supports:
- Local file storage (development/MVP)
- AWS S3 storage (production - future)
- Automatic file organization by tenant and project
- Secure file access with tenant isolation
"""

import os
import shutil
from pathlib import Path
from typing import Optional, BinaryIO
from uuid import UUID
import hashlib
from datetime import datetime

from ..core.config import settings


class StorageService:
    """
    File storage service with support for local and cloud storage.

    Local Storage Structure:
    uploads/
    └── {tenant_id}/
        └── {project_id}/
            └── {document_id}/
                └── {filename}

    This ensures tenant isolation and easy cleanup.
    """

    def __init__(self):
        """Initialize storage service."""
        self.storage_type = settings.STORAGE_TYPE  # "local" or "s3"
        self.base_path = Path(settings.UPLOAD_DIR)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _get_file_path(
        self,
        tenant_id: UUID,
        project_id: UUID,
        document_id: UUID,
        filename: str,
    ) -> Path:
        """
        Get file path for a document.

        Args:
            tenant_id: Tenant UUID
            project_id: Project UUID
            document_id: Document UUID
            filename: Original filename

        Returns:
            Path object for file location
        """
        # Sanitize filename
        safe_filename = self._sanitize_filename(filename)

        # Build path: uploads/{tenant_id}/{project_id}/{document_id}/{filename}
        file_path = (
            self.base_path
            / str(tenant_id)
            / str(project_id)
            / str(document_id)
            / safe_filename
        )

        # Create directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)

        return file_path

    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename to prevent path traversal attacks.

        Args:
            filename: Original filename

        Returns:
            Sanitized filename
        """
        # Remove any directory components
        filename = os.path.basename(filename)

        # Replace unsafe characters
        unsafe_chars = ['/', '\\', '..', '\x00']
        for char in unsafe_chars:
            filename = filename.replace(char, '_')

        return filename

    async def save_file(
        self,
        file: BinaryIO,
        tenant_id: UUID,
        project_id: UUID,
        document_id: UUID,
        filename: str,
    ) -> dict:
        """
        Save uploaded file to storage.

        Args:
            file: File object (from FastAPI UploadFile)
            tenant_id: Tenant UUID
            project_id: Project UUID
            document_id: Document UUID
            filename: Original filename

        Returns:
            Dictionary with file metadata:
            {
                "file_path": str,
                "file_size": int,
                "checksum": str,
            }
        """
        file_path = self._get_file_path(tenant_id, project_id, document_id, filename)

        # Calculate file size and checksum while saving
        file_size = 0
        checksum = hashlib.sha256()

        # Save file
        with open(file_path, "wb") as f:
            while chunk := file.read(8192):  # Read in 8KB chunks
                file_size += len(chunk)
                checksum.update(chunk)
                f.write(chunk)

        return {
            "file_path": str(file_path),
            "file_size": file_size,
            "checksum": checksum.hexdigest(),
        }

    async def get_file_path(
        self,
        tenant_id: UUID,
        project_id: UUID,
        document_id: UUID,
        filename: str,
    ) -> Optional[Path]:
        """
        Get file path if it exists.

        Args:
            tenant_id: Tenant UUID
            project_id: Project UUID
            document_id: Document UUID
            filename: Filename

        Returns:
            Path object if file exists, None otherwise
        """
        file_path = self._get_file_path(tenant_id, project_id, document_id, filename)

        if file_path.exists():
            return file_path
        return None

    async def delete_file(
        self,
        tenant_id: UUID,
        project_id: UUID,
        document_id: UUID,
        filename: str,
    ) -> bool:
        """
        Delete a file from storage.

        Args:
            tenant_id: Tenant UUID
            project_id: Project UUID
            document_id: Document UUID
            filename: Filename

        Returns:
            True if deleted, False if file didn't exist
        """
        file_path = self._get_file_path(tenant_id, project_id, document_id, filename)

        if file_path.exists():
            file_path.unlink()

            # Clean up empty directories
            try:
                # Remove document directory if empty
                file_path.parent.rmdir()
                # Remove project directory if empty
                file_path.parent.parent.rmdir()
                # Remove tenant directory if empty
                file_path.parent.parent.parent.rmdir()
            except OSError:
                # Directories not empty, that's fine
                pass

            return True
        return False

    async def delete_document_files(
        self,
        tenant_id: UUID,
        project_id: UUID,
        document_id: UUID,
    ) -> bool:
        """
        Delete all files for a document.

        Args:
            tenant_id: Tenant UUID
            project_id: Project UUID
            document_id: Document UUID

        Returns:
            True if deleted
        """
        document_dir = (
            self.base_path
            / str(tenant_id)
            / str(project_id)
            / str(document_id)
        )

        if document_dir.exists():
            shutil.rmtree(document_dir)
            return True
        return False

    async def delete_project_files(
        self,
        tenant_id: UUID,
        project_id: UUID,
    ) -> bool:
        """
        Delete all files for a project.

        Args:
            tenant_id: Tenant UUID
            project_id: Project UUID

        Returns:
            True if deleted
        """
        project_dir = self.base_path / str(tenant_id) / str(project_id)

        if project_dir.exists():
            shutil.rmtree(project_dir)
            return True
        return False

    async def get_storage_usage(
        self,
        tenant_id: UUID,
    ) -> int:
        """
        Get total storage usage for a tenant in bytes.

        Args:
            tenant_id: Tenant UUID

        Returns:
            Total bytes used
        """
        tenant_dir = self.base_path / str(tenant_id)

        if not tenant_dir.exists():
            return 0

        total_size = 0
        for file_path in tenant_dir.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size

        return total_size

    def get_allowed_extensions(self) -> list[str]:
        """
        Get list of allowed file extensions.

        Returns:
            List of allowed extensions
        """
        return [
            # Documents
            ".pdf",
            ".docx",
            ".doc",
            ".xlsx",
            ".xls",
            ".pptx",
            ".ppt",
            ".txt",
            # Images (for scanned documents)
            ".jpg",
            ".jpeg",
            ".png",
            ".tiff",
            ".tif",
            # CAD/BIM (future support)
            ".dwg",
            ".dxf",
            ".ifc",
            ".rvt",
        ]

    def is_allowed_extension(self, filename: str) -> bool:
        """
        Check if file extension is allowed.

        Args:
            filename: Filename to check

        Returns:
            True if extension is allowed
        """
        ext = Path(filename).suffix.lower()
        return ext in self.get_allowed_extensions()

    def get_mime_type(self, filename: str) -> str:
        """
        Get MIME type for a file based on extension.

        Args:
            filename: Filename

        Returns:
            MIME type string
        """
        ext = Path(filename).suffix.lower()

        mime_types = {
            ".pdf": "application/pdf",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".doc": "application/msword",
            ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ".xls": "application/vnd.ms-excel",
            ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            ".ppt": "application/vnd.ms-powerpoint",
            ".txt": "text/plain",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".tiff": "image/tiff",
            ".tif": "image/tiff",
            ".dwg": "application/acad",
            ".dxf": "application/dxf",
            ".ifc": "application/x-step",
            ".rvt": "application/x-revit",
        }

        return mime_types.get(ext, "application/octet-stream")


# Singleton instance
storage_service = StorageService()
