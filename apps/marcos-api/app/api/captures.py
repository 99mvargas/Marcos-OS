from fastapi import APIRouter, HTTPException, UploadFile

from app.models.capture import CaptureListResponse, CaptureUploadResponse
from app.services.capture_storage_service import list_recent_captures, save_capture
from app.storage.paths import CAPTURE_CATEGORIES

router = APIRouter()


@router.post("/captures/{category}", response_model=CaptureUploadResponse)
def upload_capture(category: str, file: UploadFile) -> CaptureUploadResponse:
    if category not in CAPTURE_CATEGORIES:
        raise HTTPException(status_code=404, detail=f"Unknown category: {category}")
    filename = save_capture(category, file)
    return CaptureUploadResponse(filename=filename, category=category, status="stored")


@router.get("/captures", response_model=CaptureListResponse)
def get_recent_captures() -> CaptureListResponse:
    return CaptureListResponse(items=list_recent_captures())
