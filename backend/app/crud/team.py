"""Team CRUD helpers — all async SQLAlchemy queries.

IMPORTANT — max_members race condition guard
--------------------------------------------
We use SELECT ... FOR UPDATE on the Team row to acquire a row-level advisory
lock before counting and inserting a new TeamMember.  This serialises
concurrent join attempts at the database level so that two requests hitting
the endpoint simultaneously will each see the correct member count.

Flow inside _add_member_with_lock():
  1. BEGIN (automatic with AsyncSession)
  2. SELECT * FROM teams WHERE id=? FOR UPDATE  ← acquires row lock
  3. SELECT COUNT(*) FROM team_members WHERE team_id=? AND status='active'
  4. If count >= team.max_members → raise 409 (lock released on rollback)
  5. INSERT INTO team_members ...
  6. COMMIT  ← lock released
"""

from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.join_request import TeamJoinRequest
from app.models.team import Team, TeamMember
from app.models.user import User
from app.schemas.team import TeamCreate, TeamUpdate


# ─── Internal Helpers ─────────────────────────────────────────────────────────

async def _load_team(db: AsyncSession, team_id: int) -> Team | None:
    """Load team with members and their user info eagerly."""
    result = await db.execute(
        select(Team)
        .options(
            selectinload(Team.team_members).selectinload(TeamMember.user),
            selectinload(Team.leader),
        )
        .where(Team.id == team_id)
    )
    return result.scalar_one_or_none()


async def _active_member_count(db: AsyncSession, team_id: int) -> int:
    """Count active members of a team (called INSIDE a FOR UPDATE transaction)."""
    result = await db.execute(
        select(func.count()).where(
            TeamMember.team_id == team_id,
            TeamMember.status == "active",
        )
    )
    return result.scalar_one()


async def _add_member_with_lock(
    db: AsyncSession,
    team_id: int,
    user_id: int,
    role: str = "member",
) -> TeamMember:
    """
    Insert a TeamMember inside a row-locked transaction.

    Acquires a FOR UPDATE lock on the team row, counts current active
    members, enforces max_members, then inserts — all in one atomic block.
    Raises ValueError if the team is full.
    """
    # Step 1: Lock the team row for the duration of this transaction
    locked = await db.execute(
        select(Team).where(Team.id == team_id).with_for_update()
    )
    team = locked.scalar_one_or_none()
    if team is None:
        raise ValueError("team_not_found")

    # Step 2: Count current active members (accurate because we hold the lock)
    count = await _active_member_count(db, team_id)

    # Step 3: Enforce capacity cap
    if team.max_members is not None and count >= team.max_members:
        raise ValueError("team_full")

    # Step 4: Insert
    membership = TeamMember(team_id=team_id, member_id=user_id, role=role, status="active")
    db.add(membership)
    await db.flush()
    return membership


async def get_membership(db: AsyncSession, team_id: int, user_id: int) -> TeamMember | None:
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.team_id == team_id,
            TeamMember.member_id == user_id,
        )
    )
    return result.scalar_one_or_none()


# ─── Team CRUD ────────────────────────────────────────────────────────────────

async def create_team(db: AsyncSession, data: TeamCreate, creator_id: int) -> Team:
    """Create team; creator is inserted as active leader in the same transaction."""
    team = Team(
        name=data.name,
        description=data.description,
        visibility=data.visibility,
        min_members=data.min_members,
        max_members=data.max_members,
        profile_pic=data.profile_pic,
        leader_id=creator_id,
        is_active=True,
    )
    db.add(team)
    await db.flush()  # get team.id before inserting member

    leader_membership = TeamMember(
        team_id=team.id,
        member_id=creator_id,
        role="leader",
        status="active",
    )
    db.add(leader_membership)
    await db.commit()
    return await _load_team(db, team.id)


async def get_team(db: AsyncSession, team_id: int) -> Team | None:
    return await _load_team(db, team_id)


async def get_team_by_join_code(db: AsyncSession, join_code: str) -> Team | None:
    result = await db.execute(select(Team).where(Team.join_code == join_code))
    return result.scalar_one_or_none()


async def list_teams(db: AsyncSession, skip: int = 0, limit: int = 20) -> list[Team]:
    result = await db.execute(
        select(Team)
        .options(selectinload(Team.team_members).selectinload(TeamMember.user))
        .where(Team.visibility == "public", Team.is_active == True)  # noqa: E712
        .offset(skip)
        .limit(limit)
        .order_by(Team.created_at.desc())
    )
    return list(result.scalars().all())


async def get_user_teams(db: AsyncSession, user_id: int) -> list[Team]:
    result = await db.execute(
        select(Team)
        .join(TeamMember, TeamMember.team_id == Team.id)
        .options(selectinload(Team.team_members).selectinload(TeamMember.user))
        .where(TeamMember.member_id == user_id, TeamMember.status == "active")
        .order_by(Team.created_at.desc())
    )
    return list(result.scalars().unique().all())


async def update_team(db: AsyncSession, team: Team, data: TeamUpdate) -> Team:
    update_data = data.model_dump(exclude_unset=True)
    for key, val in update_data.items():
        setattr(team, key, val)
    await db.commit()
    return await _load_team(db, team.id)


# ─── Joining ──────────────────────────────────────────────────────────────────

async def join_team_by_code(db: AsyncSession, team_id: int, user_id: int) -> TeamMember:
    """
    Join via join_code — max_members enforced at DB level with FOR UPDATE.
    Raises ValueError("team_full") or ValueError("already_member").
    """
    existing = await get_membership(db, team_id, user_id)
    if existing and existing.status == "active":
        raise ValueError("already_member")

    membership = await _add_member_with_lock(db, team_id, user_id, role="member")
    await db.commit()
    return membership


# ─── Join Requests (user → team) ─────────────────────────────────────────────

async def create_join_request(
    db: AsyncSession,
    team_id: int,
    user_id: int,
    message: str | None = None,
) -> TeamJoinRequest:
    """User requests to join a public team."""
    jr = TeamJoinRequest(
        team_id=team_id,
        user_id=user_id,
        direction="request",
        message=message,
        status="pending",
    )
    db.add(jr)
    try:
        await db.commit()
        await db.refresh(jr)
    except IntegrityError:
        await db.rollback()
        raise ValueError("request_already_exists")
    return jr


# ─── Invites (leader → user) ─────────────────────────────────────────────────

async def create_invite(
    db: AsyncSession,
    team_id: int,
    user_id: int,
    message: str | None = None,
) -> TeamJoinRequest:
    """Leader invites a user by their user_id."""
    jr = TeamJoinRequest(
        team_id=team_id,
        user_id=user_id,
        direction="invite",
        message=message,
        status="pending",
    )
    db.add(jr)
    try:
        await db.commit()
        await db.refresh(jr)
    except IntegrityError:
        await db.rollback()
        raise ValueError("invite_already_exists")
    return jr


# ─── Approve / Reject ─────────────────────────────────────────────────────────

async def get_join_request(db: AsyncSession, request_id: int) -> TeamJoinRequest | None:
    result = await db.execute(
        select(TeamJoinRequest)
        .options(selectinload(TeamJoinRequest.team), selectinload(TeamJoinRequest.user))
        .where(TeamJoinRequest.id == request_id)
    )
    return result.scalar_one_or_none()


async def process_join_request(
    db: AsyncSession,
    join_request: TeamJoinRequest,
    action: str,  # "accepted" | "rejected"
) -> TeamJoinRequest:
    """
    Accept or reject a join request / invite.

    If accepted: adds the user as an active member (with FOR UPDATE lock).
    Raises ValueError("team_full") if capacity exceeded at accept time.
    """
    if action == "accepted":
        # Check if already a member
        existing = await get_membership(db, join_request.team_id, join_request.user_id)
        if not existing or existing.status != "active":
            # Will raise ValueError("team_full") if at capacity
            await _add_member_with_lock(db, join_request.team_id, join_request.user_id)

    join_request.status = action  # "accepted" | "rejected"
    await db.commit()
    await db.refresh(join_request)
    return join_request


# ─── Remove Member ────────────────────────────────────────────────────────────

async def remove_member(db: AsyncSession, team_id: int, target_user_id: int) -> bool:
    membership = await get_membership(db, team_id, target_user_id)
    if not membership:
        return False
    await db.delete(membership)
    await db.commit()
    return True


# ─── User lookup helper for invites ───────────────────────────────────────────

async def get_user_by_name_or_email(db: AsyncSession, username: str) -> User | None:
    """Find a user by name or email (for invite-by-username flow)."""
    result = await db.execute(
        select(User).where(
            (User.email == username) | (User.name == username)
        )
    )
    return result.scalar_one_or_none()
