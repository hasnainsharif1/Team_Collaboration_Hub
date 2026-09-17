"""Join Requests API — /api/v1/join-requests

PATCH /join-requests/{id}
  - If direction='request': only the team leader can approve/reject
  - If direction='invite':  only the invited user can accept/reject
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user
from app.crud import team as crud_team
from app.db.session import get_db
from app.models.user import User
from app.schemas.team import JoinRequestAction, JoinRequestResponse

router = APIRouter()


@router.patch("/{request_id}", response_model=JoinRequestResponse)
async def process_join_request(
    request_id: int,
    payload: JoinRequestAction,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Approve or reject a TeamJoinRequest.

    Authorization rules:
    - direction='request' (user wants to join) → only the **team leader** can act
    - direction='invite'  (leader invited user) → only the **invited user** can act

    On 'accepted':
    - The user is added as an active member.
    - max_members is enforced via SELECT FOR UPDATE (same race-condition guard as join-by-code).
    - Returns 409 if team is full at the moment of acceptance.

    On 'rejected':
    - Request status is set to 'rejected'; no membership is created.
    """
    jr = await crud_team.get_join_request(db, request_id)
    if not jr:
        raise HTTPException(status_code=404, detail="Join request not found")

    if jr.status != "pending":
        raise HTTPException(
            status_code=400,
            detail=f"This request has already been {jr.status}",
        )

    # ── Authorization ──────────────────────────────────────────────────────────
    team = jr.team
    if jr.direction == "request":
        # Only the leader acts on member requests
        if team.leader_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Only the team leader can approve or reject join requests",
            )
    elif jr.direction == "invite":
        # Only the invited user acts on invites
        if jr.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Only the invited user can accept or reject this invite",
            )
    else:
        raise HTTPException(status_code=400, detail="Unknown request direction")

    # ── Process ────────────────────────────────────────────────────────────────
    try:
        updated = await crud_team.process_join_request(db, jr, payload.action)
    except ValueError as exc:
        if "team_full" in str(exc):
            raise HTTPException(
                status_code=409,
                detail="Team has reached its maximum member capacity",
            )
        raise HTTPException(status_code=400, detail=str(exc))

    return JoinRequestResponse.model_validate(updated)
