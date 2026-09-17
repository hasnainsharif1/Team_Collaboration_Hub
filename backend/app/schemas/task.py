"""Pydantic schemas for Task and TaskComment endpoints."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


# ─── Task Status ───────────────────────────────────────────────────────────────

TaskStatusLiteral = Literal["not_started", "in_progress", "done", "overdue"]


# ─── Task Comment ──────────────────────────────────────────────────────────────

class TaskCommentCreate(BaseModel):
    """Payload to add a comment on a task."""

    content: str = Field(..., min_length=1, max_length=2000)


class TaskCommentResponse(BaseModel):
    """Response schema for a task comment."""

    id: int
    task_id: int
    author_id: int | None = None
    author_name: str | None = None
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Task ──────────────────────────────────────────────────────────────────────

class TaskCreate(BaseModel):
    """Payload to create a new task."""

    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    note: str | None = Field(None, max_length=1000)
    team_id: int
    assignee_id: int | None = None
    due_date: datetime | None = None


class TaskStatusUpdate(BaseModel):
    """Payload to update a task status."""

    status: Literal["not_started", "in_progress", "done"]


class TaskResponse(BaseModel):
    """Full task response including comments."""

    id: int
    title: str
    description: str | None = None
    note: str | None = None
    status: str
    team_id: int | None = None
    assignee_id: int | None = None
    assignee_name: str | None = None
    creator_id: int | None = None
    due_date: datetime | None = None
    is_overdue: bool
    created_at: datetime
    updated_at: datetime
    comments: list[TaskCommentResponse] = []

    model_config = {"from_attributes": True}


class TaskSummary(BaseModel):
    """Compact task response for list views."""

    id: int
    title: str
    status: str
    assignee_id: int | None = None
    assignee_name: str | None = None
    team_id: int | None = None
    due_date: datetime | None = None
    is_overdue: bool
    created_at: datetime

    model_config = {"from_attributes": True}
