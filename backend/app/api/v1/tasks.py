from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def list_teams() -> list[dict[str, str]]:
    return [{"name": "example-team"}]
