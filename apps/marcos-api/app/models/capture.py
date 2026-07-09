from pydantic import BaseModel


class CaptureUploadResponse(BaseModel):
    filename: str
    category: str
    status: str


class CaptureItem(BaseModel):
    filename: str
    category: str
    uploaded_at: str


class CaptureListResponse(BaseModel):
    items: list[CaptureItem]
