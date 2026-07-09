from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def get_health() -> dict[str, str]:
    return {"status": "healthy", "service": "marcos-api", "version": "0.1"}
