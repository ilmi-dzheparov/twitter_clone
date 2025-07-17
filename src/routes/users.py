"""User-related API routes including get, follow operations."""

from fastapi import APIRouter, Depends, HTTPException, Header

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import get_async_db
from src.models import User
from src.schemas.user_schemas import (
    UserDeleteFollow,
    UserPostFollow,
    UserProfileResponse,
)

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/me", response_model=UserProfileResponse)
async def get_me(
    api_key: str = Header(..., alias="api-key"),
    db: AsyncSession = Depends(get_async_db),
) -> UserProfileResponse:
    """
    Get the profile of the current user using their API key.

    Args:
       api_key (str): The API key passed in request headers.
       db (AsyncSession): The async database session.

    Returns:
       dict: A user profile including followers and following.
    """
    res = await db.execute(
        select(User)
        .options(selectinload(User.followers), selectinload(User.following))
        .where(User.api_key == api_key)
    )
    user = res.scalars().first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return {
        "result": True,
        "user": {
            "id": user.id,
            "name": user.name,
            "followers": [{"id": u.id, "name": u.name} for u in user.followers],
            "following": [{"id": u.id, "name": u.name} for u in user.following],
        },
    }


@router.post("/{id}/follow", response_model=UserPostFollow)
async def post_follow(
    id: int,
    api_key: str = Header(..., alias="api-key"),
    db: AsyncSession = Depends(get_async_db),
) -> UserPostFollow:
    """
    Follow another user by their user ID.

    Args:
        id (int): ID of the user to follow.
        api_key (str): The current user's API key.
        db (AsyncSession): Database session dependency.

    Returns:
        dict: Result indicating success of the follow operation.
    """
    # Fetch current user by API key
    res = await db.execute(
        select(User)
        .options(selectinload(User.following))
        .where(User.api_key == api_key)
    )
    current_user = res.scalars().first()

    if not current_user:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Fetch target user to follow
    target_res = await db.execute(select(User).where(User.id == id))
    target_user = target_res.scalars().first()

    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check: cannot follow yourself
    if current_user.id == target_user.id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")

    # Check: already following the user
    if target_user in current_user.following:
        raise HTTPException(status_code=400, detail="Already following")

    # Add target user to current user's following list
    current_user.following.append(target_user)

    await db.commit()

    return {"result": True}


@router.delete("/{id}/follow", response_model=UserDeleteFollow)
async def delete_follow(
    id: int,
    api_key: str = Header(..., alias="api-key"),
    db: AsyncSession = Depends(get_async_db),
) -> UserDeleteFollow:
    """
    Unfollow a user by their user ID.

    Args:
        id (int): ID of the user to unfollow.
        api_key (str): The current user's API key.
        db (AsyncSession): Database session dependency.

    Returns:
        dict: Result indicating success of the unfollow operation.
    """
    # Fetch current user
    res = await db.execute(
        select(User)
        .options(selectinload(User.following))
        .where(User.api_key == api_key)
    )
    current_user = res.scalars().first()

    if not current_user:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Fetch target user to unfollow
    target_res = await db.execute(select(User).where(User.id == id))
    target_user = target_res.scalars().first()

    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user.id == target_user.id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")

    if target_user not in current_user.following:
        raise HTTPException(status_code=400, detail="Not yet following")

    # Remove the follow relationship
    current_user.following.remove(target_user)

    await db.commit()

    return {"result": True}


@router.get("/{id}", response_model=UserProfileResponse)
async def get_user_by_id(
        id: int, db: AsyncSession = Depends(get_async_db)
) -> UserProfileResponse:
    """
    Get a user profile by user ID.

    Args:
        id (int): ID of the user to fetch.
        db (AsyncSession): Database session dependency.

    Returns:
        dict: The user profile with followers and following lists.
    """
    res = await db.execute(
        select(User)
        .options(selectinload(User.followers), selectinload(User.following))
        .where(User.id == id)
    )
    user = res.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "result": True,
        "user": {
            "id": user.id,
            "name": user.name,
            "followers": [{"id": u.id, "name": u.name} for u in user.followers],
            "following": [{"id": u.id, "name": u.name} for u in user.following],
        },
    }
