from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def list_tasks() -> list[dict[str, str]]:
    return [{"title": "example-task"}]
