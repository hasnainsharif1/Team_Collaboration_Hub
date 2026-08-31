from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def list_feedback() -> list[dict[str, str]]:
    return [{"message": "example feedback"}]
