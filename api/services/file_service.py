from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.orm import Session

from db.models import FileRecord


class FileService:
    def __init__(self, base_dir: Path | str = "files") -> None:
        self.base_dir = Path(base_dir)

    def get_upload_dir(self, user_id: int) -> Path:
        """Return the upload directory for a given user (without creating it)."""
        return self.base_dir / str(user_id)

    async def store(self, file: UploadFile, user_id: int) -> dict:
        """Store an uploaded file on disk under files/{user_id}/ and return metadata."""

        original_name = Path(file.filename or "").name
        ext = Path(original_name).suffix

        random_name = f"{uuid4().hex}{ext}"

        user_dir = self.get_upload_dir(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)
        dest = user_dir / random_name

        content = await file.read()
        dest.write_bytes(content)

        return {
            "filename": original_name,
            "stored_filename": random_name,
            "content_type": file.content_type or "application/octet-stream",
            "size": len(content),
            "path": str(dest),
        }

    async def store_and_record(
        self,
        *,
        file: UploadFile,
        user_id: int,
        db: Session,
    ) -> FileRecord:
        """Store file on disk and create a FileRecord in the database."""
        stored = await self.store(file=file, user_id=user_id)

        record = FileRecord(
            original_name=stored["filename"],
            random_name=stored["stored_filename"],
            content_type=stored["content_type"],
            size=stored["size"],
            path=stored["path"],
            user_id=user_id,
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        return record


def get_file_service() -> FileService:
    """FastAPI dependency to provide a FileService instance."""
    return FileService()

