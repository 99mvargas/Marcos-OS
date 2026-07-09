from pydantic import BaseModel


class StatementUploadResponse(BaseModel):
    filename: str
    status: str


class StatementListResponse(BaseModel):
    filenames: list[str]
