"""Users API router for profile management and user discovery."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user
from app.crud.user import get_user, list_users, update_user_profile
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserProfileUpdate, UserResponse

router = APIRouter()


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get authenticated user profile",
)
async def get_my_profile(
    current_user: User = Depends(get_current_active_user),
) -> UserResponse:
    """Retrieve profile of the currently logged-in user."""
    return current_user


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update authenticated user profile",
)
async def update_my_profile(
    profile_in: UserProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Update profile details (name, pic, bio, skills, cv_url, links, availability).
    
    Note: The rating field is read-only and cannot be modified by the user.
    """
    updated_user = await update_user_profile(db, current_user, profile_in)
    return updated_user


@router.patch(
    "/me",
    response_model=UserResponse,
    summary="Partially update authenticated user profile",
)
async def patch_my_profile(
    profile_in: UserProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Partially update profile details for the authenticated user."""
    updated_user = await update_user_profile(db, current_user, profile_in)
    return updated_user


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user profile by ID",
)
async def get_user_profile_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
) -> UserResponse:
    """Retrieve public profile information for a specific user ID."""
    user = await get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found.",
        )
    return user


@router.get(
    "/",
    response_model=List[UserResponse],
    summary="List all users",
)
async def get_users_list(
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(20, ge=1, le=100, description="Pagination limit"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
) -> List[UserResponse]:
    """List registered users with pagination."""
    users = await list_users(db, skip=skip, limit=limit)
    return list(users)
