from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def search_items() -> dict[str, str]:
    return {"message": "search endpoint"}
