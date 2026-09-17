"""Teams API — /api/v1/teams

Endpoints:
  POST   /teams/               — create team
  POST   /teams/join/{code}    — join by code
  POST   /teams/{id}/request   — user requests to join public team
  POST   /teams/{id}/invite    — leader invites user by username
  DELETE /teams/{id}/members/{user_id} — leader removes member
  GET    /teams/{id}           — team dashboard payload
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user
from app.crud import team as crud_team
from app.db.session import get_db
from app.models.team import TeamMember
from app.models.user import User
from app.schemas.team import (
    InviteByUsernameRequest,
    JoinRequestCreate,
    JoinRequestResponse,
    TeamCreate,
    TeamMemberResponse,
    TeamResponse,
    TeamSummary,
    TeamUpdate,
)

router = APIRouter()


# ─── Schema builders ──────────────────────────────────────────────────────────

def _member_to_schema(tm: TeamMember) -> TeamMemberResponse:
    return TeamMemberResponse(
        user_id=tm.member_id,
        name=tm.user.name if tm.user else None,
        email=tm.user.email if tm.user else "",
        role=tm.role,
        status=tm.status,
        joined_at=tm.joined_at,
    )


def _team_to_response(team) -> TeamResponse:
    members = [_member_to_schema(tm) for tm in (team.team_members or [])]
    return TeamResponse(
        id=team.id,
        name=team.name,
        description=team.description,
        join_code=team.join_code,
        visibility=team.visibility,
        min_members=team.min_members,
        max_members=team.max_members,
        profile_pic=team.profile_pic,
        is_active=team.is_active,
        leader_id=team.leader_id,
        created_at=team.created_at,
        members=members,
    )


def _team_to_summary(team) -> TeamSummary:
    active_count = sum(1 for tm in (team.team_members or []) if tm.status == "active")
    return TeamSummary(
        id=team.id,
        name=team.name,
        description=team.description,
        visibility=team.visibility,
        min_members=team.min_members,
        max_members=team.max_members,
        profile_pic=team.profile_pic,
        is_active=team.is_active,
        leader_id=team.leader_id,
        member_count=active_count,
        created_at=team.created_at,
    )


# ─── Auth guards ──────────────────────────────────────────────────────────────

async def _require_leader(team_id: int, current_user: User, db: AsyncSession):
    team = await crud_team.get_team(db, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    if team.leader_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the team leader can perform this action")
    return team


async def _require_active_member(team_id: int, current_user: User, db: AsyncSession):
    team = await crud_team.get_team(db, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    membership = await crud_team.get_membership(db, team_id, current_user.id)
    if not membership or membership.status != "active":
        raise HTTPException(status_code=403, detail="You are not an active member of this team")
    return team


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    payload: TeamCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new team.
    - Auto-generates a unique join code.
    - Creator is inserted as active leader in the same DB transaction.
    """
    team = await crud_team.create_team(db, payload, creator_id=current_user.id)
    return _team_to_response(team)


@router.post("/join/{code}", response_model=TeamResponse)
async def join_by_code(
    code: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Join a team using its unique join code.

    max_members is enforced at DB transaction level (SELECT FOR UPDATE)
    to prevent race conditions when two users join simultaneously.
    """
    team = await crud_team.get_team_by_join_code(db, code.upper())
    if not team:
        raise HTTPException(status_code=404, detail="Invalid join code")
    if not team.is_active:
        raise HTTPException(status_code=400, detail="This team is no longer accepting members")

    try:
        await crud_team.join_team_by_code(db, team.id, current_user.id)
    except ValueError as exc:
        if "team_full" in str(exc):
            raise HTTPException(status_code=409, detail="Team has reached its maximum member capacity")
        if "already_member" in str(exc):
            raise HTTPException(status_code=400, detail="You are already an active member of this team")
        raise HTTPException(status_code=400, detail=str(exc))

    refreshed = await crud_team.get_team(db, team.id)
    return _team_to_response(refreshed)


@router.post("/{team_id}/request", response_model=JoinRequestResponse, status_code=status.HTTP_201_CREATED)
async def request_to_join(
    team_id: int,
    payload: JoinRequestCreate = JoinRequestCreate(),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    User requests to join a public team.
    Creates a TeamJoinRequest with direction='request' and status='pending'.
    Leader approves or rejects via PATCH /join-requests/{id}.
    """
    team = await crud_team.get_team(db, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    if team.visibility != "public":
        raise HTTPException(status_code=400, detail="Use the join code to join private teams")
    if not team.is_active:
        raise HTTPException(status_code=400, detail="This team is not accepting requests")

    # Check already a member
    existing = await crud_team.get_membership(db, team_id, current_user.id)
    if existing and existing.status == "active":
        raise HTTPException(status_code=400, detail="You are already an active member of this team")

    try:
        jr = await crud_team.create_join_request(db, team_id, current_user.id, payload.message)
    except ValueError as exc:
        if "already_exists" in str(exc):
            raise HTTPException(status_code=409, detail="You already have a pending join request for this team")
        raise HTTPException(status_code=400, detail=str(exc))

    return JoinRequestResponse.model_validate(jr)


@router.post("/{team_id}/invite", response_model=JoinRequestResponse, status_code=status.HTTP_201_CREATED)
async def invite_user(
    team_id: int,
    payload: InviteByUsernameRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Leader invites a user to join the team by their name or email.
    Creates a TeamJoinRequest with direction='invite' and status='pending'.
    The invited user accepts/rejects via PATCH /join-requests/{id}.
    """
    await _require_leader(team_id, current_user, db)

    # Lookup target user
    target_user = await crud_team.get_user_by_name_or_email(db, payload.username)
    if not target_user:
        raise HTTPException(status_code=404, detail=f"User '{payload.username}' not found")

    # Already a member?
    existing = await crud_team.get_membership(db, team_id, target_user.id)
    if existing and existing.status == "active":
        raise HTTPException(status_code=400, detail="User is already an active member of this team")

    try:
        jr = await crud_team.create_invite(db, team_id, target_user.id, payload.message)
    except ValueError as exc:
        if "already_exists" in str(exc):
            raise HTTPException(status_code=409, detail="An invite for this user already exists")
        raise HTTPException(status_code=400, detail=str(exc))

    return JoinRequestResponse.model_validate(jr)


@router.delete("/{team_id}/members/{user_id}", response_model=dict)
async def remove_member(
    team_id: int,
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Remove a member from the team. Leader only.
    Leader cannot remove themselves — they must transfer leadership first.
    """
    team = await _require_leader(team_id, current_user, db)
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Leader cannot remove themselves from the team")

    removed = await crud_team.remove_member(db, team_id, user_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Member not found in this team")
    return {"message": f"User {user_id} has been removed from the team"}


@router.get("/{team_id}", response_model=TeamResponse)
async def get_team_dashboard(
    team_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Team dashboard payload — full member list + team details.
    The join_code is visible to all authenticated users (they need it to share).
    """
    team = await crud_team.get_team(db, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return _team_to_response(team)


@router.get("/", response_model=list[TeamSummary])
async def list_public_teams(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List active public teams (paginated)."""
    teams = await crud_team.list_teams(db, skip=skip, limit=limit)
    return [_team_to_summary(t) for t in teams]


@router.get("/my", response_model=list[TeamSummary])
async def list_my_teams(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List all teams the current user is an active member of."""
    teams = await crud_team.get_user_teams(db, user_id=current_user.id)
    return [_team_to_summary(t) for t in teams]


@router.put("/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: int,
    payload: TeamUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update team metadata. Leader only."""
    team = await _require_leader(team_id, current_user, db)
    updated = await crud_team.update_team(db, team, payload)
    return _team_to_response(updated)
