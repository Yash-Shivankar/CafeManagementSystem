import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.core.config import settings
from app.schemas.auth import MediaUrlRequestSchema, MediaUrlSchema
from app.utils.media import UnsafeMediaPath, resolve_media_path, sign_media_path

router = APIRouter(prefix="/common", tags=["Commons"])

ALLOWED_CONTENT_TYPES = {
    "application/pdf": "pdf",
    "application/msword": "doc",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "text/plain": "txt",
    "application/vnd.ms-excel": "excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "excel",
    "text/csv": "csv",
}

MAX_FILE_SIZE = 10 * 1024 * 1024


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
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type",
        )

    file_size = get_file_size(file)
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File too large (max 10MB)",
        )

    subfolder = resolve_upload_folder(file)
    upload_dir = settings.MEDIA_ROOT / "documents" / subfolder
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_ext = Path(file.filename).suffix
    filename = f"{uuid4().hex}{file_ext}"
    file_path = upload_dir / filename

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


@router.post("/media-url", response_model=MediaUrlSchema)
def create_media_url(payload: MediaUrlRequestSchema):
    """Mint a short-lived signed URL for a stored file.

    `<img src>` and download anchors cannot carry an Authorization header, so
    the SPA calls this first — behind the normal auth guard — and then uses
    the returned URL, which is bound to this one path and expires in minutes.
    """
    relative = payload.path.replace("\\", "/").lstrip("/")
    if relative.startswith("media/"):
        relative = relative[len("media/") :]

    try:
        resolved = resolve_media_path(relative)
    except UnsafeMediaPath as exc:
        raise HTTPException(status_code=400, detail="Invalid path") from exc

    if not resolved.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    signature, expires_at = sign_media_path(relative)

    return {
        "url": f"{settings.MEDIA_URL}{relative}?sig={signature}&exp={expires_at}",
        "expires_at": expires_at,
    }
