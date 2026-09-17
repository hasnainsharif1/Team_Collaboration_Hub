"""Tasks API — /api/v1/tasks"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user
from app.crud import task as crud_task
from app.crud import team as crud_team
from app.db.session import get_db
from app.models.task import Task, TaskComment
from app.models.user import User
from app.schemas.task import (
    TaskCommentCreate,
    TaskCommentResponse,
    TaskCreate,
    TaskResponse,
    TaskStatusUpdate,
    TaskSummary,
)

router = APIRouter()


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _comment_to_schema(c: TaskComment) -> TaskCommentResponse:
    return TaskCommentResponse(
        id=c.id,
        task_id=c.task_id,
        author_id=c.author_id,
        author_name=c.author.name if c.author else None,
        content=c.content,
        created_at=c.created_at,
    )


def _task_to_response(task: Task) -> TaskResponse:
    comments = [_comment_to_schema(c) for c in (task.comments or [])]
    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        note=task.note,
        status=task.status,
        team_id=task.team_id,
        assignee_id=task.assignee_id,
        assignee_name=task.assignee.name if task.assignee else None,
        creator_id=task.creator_id,
        due_date=task.due_date,
        is_overdue=task.is_overdue,
        created_at=task.created_at,
        updated_at=task.updated_at,
        comments=comments,
    )


def _task_to_summary(task: Task) -> TaskSummary:
    return TaskSummary(
        id=task.id,
        title=task.title,
        status=task.status,
        assignee_id=task.assignee_id,
        assignee_name=task.assignee.name if task.assignee else None,
        team_id=task.team_id,
        due_date=task.due_date,
        is_overdue=task.is_overdue,
        created_at=task.created_at,
    )


async def _verify_team_membership(db: AsyncSession, team_id: int, user_id: int) -> None:
    """Raise 403 if user is not an active member of the team."""
    membership = await crud_team._is_member(db, team_id, user_id)
    if not membership or membership.status != "active":
        raise HTTPException(status_code=403, detail="You are not an active member of this team")


async def _get_task_or_404(db: AsyncSession, task_id: int) -> Task:
    task = await crud_task.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    payload: TaskCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new task within a team.
    Creator must be an active team member.
    Optionally assign to another team member.
    """
    # Verify creator is a member
    await _verify_team_membership(db, payload.team_id, current_user.id)

    # If assigning to someone else, verify they're also a member
    if payload.assignee_id and payload.assignee_id != current_user.id:
        await _verify_team_membership(db, payload.team_id, payload.assignee_id)

    task = await crud_task.create_task(db, payload, creator_id=current_user.id)
    return _task_to_response(task)


@router.get("/", response_model=list[TaskSummary])
async def list_my_tasks(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List all tasks assigned to the current user."""
    tasks = await crud_task.list_user_tasks(db, user_id=current_user.id)
    return [_task_to_summary(t) for t in tasks]


@router.get("/team/{team_id}", response_model=list[TaskSummary])
async def list_team_tasks(
    team_id: int,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List all tasks for a team. Active members only."""
    await _verify_team_membership(db, team_id, current_user.id)
    tasks = await crud_task.list_team_tasks(db, team_id=team_id, skip=skip, limit=limit)
    return [_task_to_summary(t) for t in tasks]


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a task with its full comment history. User must be a team member."""
    task = await _get_task_or_404(db, task_id)
    if task.team_id:
        await _verify_team_membership(db, task.team_id, current_user.id)
    return _task_to_response(task)


@router.patch("/{task_id}/status", response_model=TaskResponse)
async def update_task_status(
    task_id: int,
    payload: TaskStatusUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update task status (not_started → in_progress → done).
    Only the assignee or the team leader can update status.
    """
    task = await _get_task_or_404(db, task_id)

    if task.team_id:
        membership = await crud_team._is_member(db, task.team_id, current_user.id)
        if not membership or membership.status != "active":
            raise HTTPException(status_code=403, detail="Not a team member")

        # Must be assignee or leader
        team = await crud_team.get_team(db, task.team_id)
        is_leader = team and team.leader_id == current_user.id
        is_assignee = task.assignee_id == current_user.id

        if not (is_leader or is_assignee):
            raise HTTPException(
                status_code=403,
                detail="Only the task assignee or team leader can update status",
            )

    updated = await crud_task.update_task_status(db, task, payload.status)
    return _task_to_response(updated)


@router.post("/{task_id}/comments", response_model=TaskCommentResponse, status_code=status.HTTP_201_CREATED)
async def add_comment(
    task_id: int,
    payload: TaskCommentCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a comment to a task. Active team members only."""
    task = await _get_task_or_404(db, task_id)
    if task.team_id:
        await _verify_team_membership(db, task.team_id, current_user.id)

    comment = await crud_task.add_task_comment(
        db, task_id=task_id, author_id=current_user.id, content=payload.content
    )
    return _comment_to_schema(comment)
