"""User SQLAlchemy ORM Model."""

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, JSON, String, Text, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="user", nullable=False)  # superadmin, admin, user
    name = Column(String(255), nullable=True)
    profile_pic = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    skills = Column(JSON, default=list, nullable=True)
    cv_url = Column(String(500), nullable=True)
    website = Column(String(255), nullable=True)
    social_links = Column(JSON, default=dict, nullable=True)
    availability = Column(String(50), default="available", nullable=False)  # available, busy, unavailable
    is_active = Column(Boolean, default=True, nullable=False)
    rating = Column(Float, default=0.0, nullable=False)  # Computed in Phase 4 (read-only for user)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    led_teams = relationship("Team", foreign_keys="Team.leader_id", back_populates="leader")
    team_memberships = relationship("TeamMember", back_populates="user", cascade="all, delete-orphan")
    join_requests = relationship("TeamJoinRequest", back_populates="user", cascade="all, delete-orphan")
    assigned_tasks = relationship("Task", foreign_keys="Task.assignee_id", back_populates="assignee")
    created_tasks = relationship("Task", foreign_keys="Task.creator_id", back_populates="creator")
    task_comments = relationship("TaskComment", back_populates="author")
    notifications = relationship("Notification", back_populates="user")
