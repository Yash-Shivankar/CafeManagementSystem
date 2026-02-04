from fastapi import APIRouter, Depends, Query
from fastapi import UploadFile, File, HTTPException, status
from pathlib import Path
from uuid import uuid4
import shutil

from app.core.config import settings

router = APIRouter(prefix="/common", tags=["Commons"])

# Allowed MIME types
ALLOWED_CONTENT_TYPES = {
    # Documents
    "application/pdf": "pdf",
    "application/msword": "doc",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "text/plain": "txt",
    # Excel / CSV
    "application/vnd.ms-excel": "excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "excel",
    "text/csv": "csv",
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def get_file_size(file: UploadFile) -> int:
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    return size


def resolve_upload_folder(file: UploadFile) -> str:
    content_type = file.content_type

    if content_type.startswith("image/"):
        return "images"

    if content_type in ALLOWED_CONTENT_TYPES:
        return ALLOWED_CONTENT_TYPES[content_type]

    return "others"


@router.post("/upload/document/", status_code=status.HTTP_201_CREATED)
async def upload_document(file: UploadFile = File(...)):
    # Validate content type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type",
        )

    # Validate file size
    file_size = get_file_size(file)
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File too large (max 10MB)",
        )

    # Determine subfolder
    subfolder = resolve_upload_folder(file)
    upload_dir = settings.MEDIA_ROOT / "documents" / subfolder
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Safe unique filename
    file_ext = Path(file.filename).suffix
    filename = f"{uuid4().hex}{file_ext}"
    file_path = upload_dir / filename

    # Save file
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        file.file.close()

    return {
        "filename": filename,
        "original_name": file.filename,
        "content_type": file.content_type,
        "size": file_size,
        "doc_url": f"/media/documents/{subfolder}/{filename}",
    }
