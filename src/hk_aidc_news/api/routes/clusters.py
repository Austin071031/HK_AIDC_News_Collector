from fastapi import APIRouter

router = APIRouter(prefix="/api/clusters", tags=["clusters"])


@router.get("")
def list_clusters() -> dict[str, list]:
    return {"items": []}
