from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def admin_dashboard() -> dict[str, str]:
    return {"message": "admin dashboard"}
