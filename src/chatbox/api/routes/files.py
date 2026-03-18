from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from chatbox.api.services.file_service import FileService, get_file_service
from chatbox.db.database import get_db
from chatbox.db.models import UserRecord
from chatbox.utils.auth import get_current_user

router = APIRouter(prefix="/files", tags=["files"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    current_user: UserRecord = Depends(get_current_user),
    file_service: FileService = Depends(get_file_service),
    db: Session = Depends(get_db),
):
    """Upload a file. Stored under files/{user_id}/ and record metadata in DB."""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required",
        )

    record = await file_service.store_and_record(
        file=file,
        user_id=current_user.id,
        db=db,
    )

    return {
        "id": record.id,
        "original_name": record.original_name,
        "random_name": record.random_name,
        "content_type": record.content_type,
        "size": record.size,
        "user_id": record.user_id,
        "created_at": record.created_at,
        "path": record.path,
    }


@router.get("/search_content")
def search_content(
    q: str,
    limit: int = 20,
    offset: int = 0,
    current_user: UserRecord = Depends(get_current_user),
    file_service: FileService = Depends(get_file_service),
    db: Session = Depends(get_db),
):
    """Search within indexed file content and return ranked results (current user only)."""
    q = (q or "").strip()
    if not q:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query parameter 'q' is required",
        )

    limit = max(1, min(limit, 100))
    offset = max(0, offset)

    results = file_service.search_content(
        query=q,
        user_id=current_user.id,
        db=db,
        limit=limit,
        offset=offset,
    )

    return {
        "query": q,
        "limit": limit,
        "offset": offset,
        "results": results,
    }