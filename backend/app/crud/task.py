"""Task CRUD helpers — all async SQLAlchemy queries."""

from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.task import Task, TaskComment
from app.schemas.task import TaskCreate


# ─── Helpers ──────────────────────────────────────────────────────────────────

async def _get_task_with_comments(db: AsyncSession, task_id: int) -> Task | None:
    """Load a task eagerly with its comments and comment authors."""
    result = await db.execute(
        select(Task)
        .options(
            selectinload(Task.comments).selectinload(TaskComment.author),
            selectinload(Task.assignee),
            selectinload(Task.creator),
        )
        .where(Task.id == task_id)
    )
    return result.scalar_one_or_none()


# ─── Create ───────────────────────────────────────────────────────────────────

async def create_task(db: AsyncSession, data: TaskCreate, creator_id: int) -> Task:
    """Create a new task in a team."""
    task = Task(
        title=data.title,
        description=data.description,
        note=data.note,
        team_id=data.team_id,
        assignee_id=data.assignee_id,
        creator_id=creator_id,
        due_date=data.due_date,
        status="not_started",
        is_overdue=False,
    )
    db.add(task)
    await db.commit()
    return await _get_task_with_comments(db, task.id)


# ─── Read ─────────────────────────────────────────────────────────────────────

async def get_task(db: AsyncSession, task_id: int) -> Task | None:
    return await _get_task_with_comments(db, task_id)


async def list_team_tasks(
    db: AsyncSession, team_id: int, skip: int = 0, limit: int = 50
) -> list[Task]:
    """List all tasks for a specific team."""
    result = await db.execute(
        select(Task)
        .options(selectinload(Task.assignee))
        .where(Task.team_id == team_id)
        .order_by(Task.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def list_user_tasks(db: AsyncSession, user_id: int) -> list[Task]:
    """List all tasks assigned to a specific user."""
    result = await db.execute(
        select(Task)
        .options(selectinload(Task.assignee))
        .where(Task.assignee_id == user_id)
        .order_by(Task.created_at.desc())
    )
    return list(result.scalars().all())


# ─── Update ───────────────────────────────────────────────────────────────────

async def update_task_status(
    db: AsyncSession, task: Task, new_status: str
) -> Task:
    """Update a task's status. If marked done, clear overdue flag."""
    task.status = new_status
    if new_status == "done":
        task.is_overdue = False
    await db.commit()
    return await _get_task_with_comments(db, task.id)


# ─── Comments ─────────────────────────────────────────────────────────────────

async def add_task_comment(
    db: AsyncSession, task_id: int, author_id: int, content: str
) -> TaskComment:
    """Append a comment to a task."""
    comment = TaskComment(task_id=task_id, author_id=author_id, content=content)
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    # reload with author
    result = await db.execute(
        select(TaskComment)
        .options(selectinload(TaskComment.author))
        .where(TaskComment.id == comment.id)
    )
    return result.scalar_one()


# ─── Background Overdue Checker ───────────────────────────────────────────────

async def mark_overdue_tasks(db: AsyncSession) -> int:
    """
    Bulk-flag all non-done tasks whose due_date has passed as overdue.
    Returns the number of tasks updated.
    """
    now = datetime.now(tz=timezone.utc)
    result = await db.execute(
        update(Task)
        .where(
            Task.due_date < now,
            Task.status.not_in(["done", "overdue"]),
        )
        .values(status="overdue", is_overdue=True)
        .execution_options(synchronize_session="fetch")
    )
    await db.commit()
    return result.rowcount
