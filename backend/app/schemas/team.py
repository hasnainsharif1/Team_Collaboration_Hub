"""Pydantic schemas for Team, TeamMember, and TeamJoinRequest endpoints."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


# ─── Team Member ───────────────────────────────────────────────────────────────

class TeamMemberResponse(BaseModel):
    """Public view of a single team member."""

    user_id: int
    name: str | None = None
    email: str
    role: Literal["leader", "member"]
    status: Literal["active", "pending"]
    joined_at: datetime

    model_config = {"from_attributes": True}


# ─── Team Create / Update ──────────────────────────────────────────────────────

class TeamCreate(BaseModel):
    """Payload to create a new team."""

    name: str = Field(..., min_length=2, max_length=255)
    description: str | None = Field(None, max_length=1000)
    visibility: Literal["public", "private"] = "private"
    min_members: int = Field(1, ge=1, description="Minimum expected team size")
    max_members: int | None = Field(None, ge=2, description="Hard cap on active members (None = unlimited)")
    profile_pic: str | None = Field(None, max_length=500, description="Team avatar URL")


class TeamUpdate(BaseModel):
    """Payload to update team info (leader only)."""

    name: str | None = Field(None, min_length=2, max_length=255)
    description: str | None = Field(None, max_length=1000)
    visibility: Literal["public", "private"] | None = None
    min_members: int | None = Field(None, ge=1)
    max_members: int | None = Field(None, ge=2)
    profile_pic: str | None = Field(None, max_length=500)
    is_active: bool | None = None


# ─── Team Responses ────────────────────────────────────────────────────────────

class TeamResponse(BaseModel):
    """Full team dashboard payload including member list."""

    id: int
    name: str
    description: str | None = None
    join_code: str
    visibility: str
    min_members: int
    max_members: int | None = None
    profile_pic: str | None = None
    is_active: bool
    leader_id: int | None = None
    created_at: datetime
    members: list[TeamMemberResponse] = []

    model_config = {"from_attributes": True}


class TeamSummary(BaseModel):
    """Compact team view for listing endpoints."""

    id: int
    name: str
    description: str | None = None
    visibility: str
    min_members: int
    max_members: int | None = None
    profile_pic: str | None = None
    is_active: bool
    leader_id: int | None = None
    member_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Join Request / Invite Schemas ────────────────────────────────────────────

class JoinRequestCreate(BaseModel):
    """Optional message when requesting to join a public team."""

    message: str | None = Field(None, max_length=500)


class InviteByUsernameRequest(BaseModel):
    """Leader invites a user to join a team by their name or email."""

    username: str = Field(..., description="The target user's name or email")
    message: str | None = Field(None, max_length=500)


class JoinRequestAction(BaseModel):
    """Body for approving or rejecting a join request or invite."""

    action: Literal["accepted", "rejected"]


class JoinRequestResponse(BaseModel):
    """Full join request / invite response."""

    id: int
    team_id: int
    user_id: int
    direction: Literal["request", "invite"]
    message: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
