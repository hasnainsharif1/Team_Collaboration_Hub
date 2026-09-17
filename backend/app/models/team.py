"""Team & TeamMember SQLAlchemy ORM Models."""

import secrets
import string

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.db.base import Base


def _generate_join_code(length: int = 8) -> str:
    """Generate a random alphanumeric join code."""
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


class TeamMember(Base):
    """Association model tracking team membership with role and approval status."""

    __tablename__ = "team_members"

    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), primary_key=True)
    member_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)

    # leader | member
    role = Column(String(20), nullable=False, default="member")
    # active | pending
    status = Column(String(20), nullable=False, default="active")

    joined_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    team = relationship("Team", back_populates="team_members")
    user = relationship("User", back_populates="team_memberships")


class Team(Base):
    """Team model with join code, visibility control, and member capacity limits."""

    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)

    # Minimum number of members expected (informational, for display)
    min_members = Column(Integer, nullable=False, default=1)
    # Maximum active members allowed (None = unlimited).
    # Enforced at DB transaction level via SELECT FOR UPDATE in CRUD.
    max_members = Column(Integer, nullable=True)

    # Team avatar/logo URL
    profile_pic = Column(String(500), nullable=True)

    # Whether the team is accepting new members / is visible
    is_active = Column(Boolean, nullable=False, default=True)

    # Auto-generated unique invite code (e.g. "A3X9KP2M")
    join_code = Column(String(12), unique=True, index=True, nullable=False, default=_generate_join_code)

    # public | private
    visibility = Column(String(20), nullable=False, default="private")

    # The user who created and leads the team
    leader_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    leader = relationship("User", foreign_keys=[leader_id], back_populates="led_teams")
    team_members = relationship(
        "TeamMember",
        back_populates="team",
        cascade="all, delete-orphan",
    )
    join_requests = relationship(
        "TeamJoinRequest",
        back_populates="team",
        cascade="all, delete-orphan",
    )
    tasks = relationship("Task", back_populates="team", cascade="all, delete-orphan")
