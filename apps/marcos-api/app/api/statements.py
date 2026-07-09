from fastapi import APIRouter, UploadFile

from app.models.statement import StatementListResponse, StatementUploadResponse
from app.services.statement_storage_service import list_statements, save_statement

router = APIRouter()


@router.post("/statements", response_model=StatementUploadResponse)
def upload_statement(file: UploadFile) -> StatementUploadResponse:
    filename = save_statement(file)
    return StatementUploadResponse(filename=filename, status="stored")


@router.get("/statements", response_model=StatementListResponse)
def get_statements() -> StatementListResponse:
    return StatementListResponse(filenames=list_statements())
