"""Services."""

from fastapi import HTTPException

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models import User


async def get_user_by_api_key(api_key: str, db: AsyncSession) -> User:
    """Get user by API key."""
    res = await db.execute(
        select(User)
        .options(selectinload(User.following))
        .where(User.api_key == api_key)
    )
    user = res.scalars().first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return user
