"""User Pydantic Schemas."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRole(str, Enum):
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    USER = "user"


class AvailabilityStatus(str, Enum):
    AVAILABLE = "available"
    BUSY = "busy"
    UNAVAILABLE = "unavailable"


class UserBase(BaseModel):
    email: EmailStr
    name: str | None = None
    role: UserRole = UserRole.USER
    bio: str | None = None
    skills: list[str] = Field(default_factory=list)
    cv_url: str | None = None
    website: str | None = None
    social_links: dict[str, str] = Field(default_factory=dict)
    availability: AvailabilityStatus = AvailabilityStatus.AVAILABLE


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, description="Password with minimum 6 characters")
    name: str | None = None
    role: UserRole = UserRole.USER
    bio: str | None = None
    skills: list[str] = Field(default_factory=list)
    cv_url: str | None = None
    website: str | None = None
    social_links: dict[str, str] = Field(default_factory=dict)
    availability: AvailabilityStatus = AvailabilityStatus.AVAILABLE


class UserProfileUpdate(BaseModel):
    """Fields allowed to be updated by a regular user on their profile."""
    name: str | None = None
    profile_pic: str | None = None
    bio: str | None = None
    skills: list[str] | None = None
    cv_url: str | None = None
    website: str | None = None
    social_links: dict[str, str] | None = None
    availability: AvailabilityStatus | None = None


class UserAdminUpdate(BaseModel):
    """Fields updatable by an admin or superadmin."""
    name: str | None = None
    role: UserRole | None = None
    is_active: bool | None = None
    availability: AvailabilityStatus | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    name: str | None = None
    role: str
    profile_pic: str | None = None
    bio: str | None = None
    skills: list[str] = Field(default_factory=list)
    cv_url: str | None = None
    website: str | None = None
    social_links: dict[str, Any] = Field(default_factory=dict)
    availability: str
    is_active: bool
    rating: float = 0.0  # Read-only, computed in Phase 4
    created_at: datetime
    updated_at: datetime
