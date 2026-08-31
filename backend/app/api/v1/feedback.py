from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def list_files() -> list[dict[str, str]]:
    return [{"name": "example-file"}]
