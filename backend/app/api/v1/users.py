from fastapi import APIRouter

router = APIRouter()


@router.get("/me")
def get_me() -> dict[str, str]:
    return {"message": "Auth endpoint"}
