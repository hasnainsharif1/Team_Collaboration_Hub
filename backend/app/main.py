from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1 import admin, auth, feedback, files, notifications, search, tasks, teams, users, ws
from app.core.config import get_settings
from app.db.session import get_db

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if settings.CORS_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(teams.router, prefix="/api/v1/teams", tags=["teams"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["tasks"])
app.include_router(files.router, prefix="/api/v1/files", tags=["files"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["notifications"])
app.include_router(feedback.router, prefix="/api/v1/feedback", tags=["feedback"])
app.include_router(search.router, prefix="/api/v1/search", tags=["search"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(ws.router, prefix="/ws", tags=["websocket"])


@app.get("/", tags=["root"])
async def read_root() -> dict[str, str]:
    """Root endpoint returning basic welcome payload."""
    return {"message": f"Welcome to {settings.APP_NAME} API"}


@app.get("/health", tags=["health"])
async def health_check(db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    """Health check endpoint confirming application runtime and database connectivity."""
    health_status = {
        "status": "healthy",
        "environment": settings.ENV,
        "database": "disconnected",
    }

    try:
        result = await db.execute(text("SELECT 1"))
        if result.scalar() == 1:
            health_status["database"] = "connected"
    except Exception as exc:
        health_status["status"] = "unhealthy"
        health_status["database_error"] = str(exc)

    return health_status
