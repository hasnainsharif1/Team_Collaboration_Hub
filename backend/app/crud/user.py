"""User CRUD database operations."""

from typing import Any, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import UserAdminUpdate, UserCreate, UserProfileUpdate


async def get_user(db: AsyncSession, user_id: int) -> User | None:
    """Retrieve a single user by primary key ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Retrieve a single user by email address."""
    result = await db.execute(select(User).where(User.email == email.lower().strip()))
    return result.scalars().first()


async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    """Create a new user with hashed password."""
    hashed_pw = get_password_hash(user_in.password)
    db_user = User(
        email=user_in.email.lower().strip(),
        hashed_password=hashed_pw,
        name=user_in.name,
        role=user_in.role.value if hasattr(user_in.role, "value") else str(user_in.role),
        bio=user_in.bio,
        skills=user_in.skills or [],
        cv_url=user_in.cv_url,
        website=user_in.website,
        social_links=user_in.social_links or {},
        availability=user_in.availability.value if hasattr(user_in.availability, "value") else str(user_in.availability),
        is_active=True,
        rating=0.0,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def update_user_profile(
    db: AsyncSession,
    db_user: User,
    profile_in: UserProfileUpdate | dict[str, Any],
) -> User:
    """Update non-sensitive profile fields of an existing user."""
    update_data = profile_in if isinstance(profile_in, dict) else profile_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        if value is not None:
            if hasattr(value, "value"):
                value = value.value
            setattr(db_user, field, value)

    await db.commit()
    await db.refresh(db_user)
    return db_user


async def update_user_admin(
    db: AsyncSession,
    db_user: User,
    admin_in: UserAdminUpdate | dict[str, Any],
) -> User:
    """Update administrative fields (role, active status, etc.)."""
    update_data = admin_in if isinstance(admin_in, dict) else admin_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        if value is not None:
            if hasattr(value, "value"):
                value = value.value
            setattr(db_user, field, value)

    await db.commit()
    await db.refresh(db_user)
    return db_user


async def update_password(db: AsyncSession, db_user: User, new_hashed_password: str) -> User:
    """Update user's password hash."""
    db_user.hashed_password = new_hashed_password
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def list_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> Sequence[User]:
    """List users with offset and limit pagination."""
    result = await db.execute(select(User).offset(skip).limit(limit).order_by(User.id))
    return result.scalars().all()
