"""Core configuration settings."""

from functools import lru_cache
<<<<<<< HEAD
from pathlib import Path
from typing import List, Union

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Dynamically locate the .env file in the backend directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE_PATH = BASE_DIR / ".env"


class Settings(BaseSettings):
    """Application Settings loaded automatically from .env environment variables."""
=======
from typing import List, Union

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
>>>>>>> c711996c105a3a218b7343120a357543694e6be9
    APP_NAME: str = "Team Collaboration Hub"
    ENV: str = "development"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/team_collaboration"
    SECRET_KEY: str = "change-me-in-production-super-secret-key-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173"]

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Union[str, None]) -> str:
        if isinstance(v, str):
            if v.startswith("postgresql://"):
                return v.replace("postgresql://", "postgresql+asyncpg://", 1)
            elif v.startswith("postgres://"):
                return v.replace("postgres://", "postgresql+asyncpg://", 1)
            return v
        return "postgresql+asyncpg://postgres:postgres@localhost:5432/team_collaboration"

    model_config = SettingsConfigDict(
<<<<<<< HEAD
        env_file=str(ENV_FILE_PATH),
=======
        env_file=".env",
>>>>>>> c711996c105a3a218b7343120a357543694e6be9
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

