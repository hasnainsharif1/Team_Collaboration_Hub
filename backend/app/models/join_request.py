"""TeamJoinRequest SQLAlchemy ORM Model.

Tracks two-directional membership flows:
  - direction="request" : user asks to join a public team (leader approves/rejects)
  - direction="invite"  : leader invites a user by username (user accepts/rejects)
"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class TeamJoinRequest(Base):
    """Represents a pending join request or leader invite for a team."""

    __tablename__ = "team_join_requests"

    id = Column(Integer, primary_key=True, index=True)

    team_id = Column(
        Integer,
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # "request" — user initiated | "invite" — leader initiated
    direction = Column(String(10), nullable=False)

    # Optional note from the requester or inviting leader
    message = Column(Text, nullable=True)

    # pending | accepted | rejected
    status = Column(String(10), nullable=False, default="pending")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    team = relationship("Team", back_populates="join_requests")
    user = relationship("User", back_populates="join_requests")

    # Prevent duplicate open requests in the same direction
    __table_args__ = (
        UniqueConstraint("team_id", "user_id", "direction", name="uq_join_request_team_user_direction"),
    )
