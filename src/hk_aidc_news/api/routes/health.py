from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    # Keep the first route tiny: it doubles as a readiness probe and test target.
    return {"status": "ok"}
