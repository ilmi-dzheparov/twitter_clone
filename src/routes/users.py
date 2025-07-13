from fastapi import APIRouter, Header, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.database import get_async_db
from src.models import User
from src.schemas.tweet_schemas import TweetPostLikeResponse
from src.schemas.user_schemas import UserProfileResponse, UserPostFollow, UserDeleteFollow

router = APIRouter(prefix="/api/users", tags=["Users"])

@router.get("/me", response_model=UserProfileResponse)
async def get_me(api_key: str = Header(..., alias="api-key"), db: AsyncSession = Depends(get_async_db)):
    res = await db.execute(
        select(User)
        .options(
            selectinload(User.followers),
            selectinload(User.following)
        )
        .where(User.api_key == api_key))
    user = res.scalars().first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return {
        "result": "true",
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
        db: AsyncSession = Depends(get_async_db)
):
    # Получаем текущего пользователя по api_key
    res = await db.execute(
        select(User)
        .options(selectinload(User.following))
        .where(User.api_key == api_key)
    )
    current_user = res.scalars().first()

    if not current_user:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Получаем пользователя, на которого хотим подписаться
    target_res = await db.execute(select(User).where(User.id == id))
    target_user = target_res.scalars().first()

    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Проверка: нельзя подписаться на самого себя
    if current_user.id == target_user.id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")

    # Проверка: уже подписан
    if target_user in current_user.following:
        raise HTTPException(status_code=400, detail="Already following")

    # Добавляем подписку
    current_user.following.append(target_user)

    await db.commit()

    return {"result": True}


@router.delete("/{id}/follow", response_model=UserPostFollow)
async def delete_follow(
        id: int,
        api_key: str = Header(..., alias="api-key"),
        db: AsyncSession = Depends(get_async_db)
):
    # Получаем текущего пользователя по api_key
    res = await db.execute(
        select(User)
        .options(selectinload(User.following))
        .where(User.api_key == api_key)
    )
    current_user = res.scalars().first()

    if not current_user:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Получаем пользователя, на которого хотим подписаться
    target_res = await db.execute(select(User).where(User.id == id))
    target_user = target_res.scalars().first()

    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Проверка: нельзя подписаться на самого себя
    if current_user.id == target_user.id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")

    # Проверка: уже подписан
    if target_user not in current_user.following:
        raise HTTPException(status_code=400, detail="Not yet following")

    # Добавляем подписку
    current_user.following.remove(target_user)

    await db.commit()

    return {"result": True}


@router.get("/{id}", response_model=UserProfileResponse)
async def get_me(
        id: int,
        db: AsyncSession = Depends(get_async_db)
):
    res = await db.execute(
        select(User)
        .options(
            selectinload(User.followers),
            selectinload(User.following)
        )
        .where(User.id == id))
    user = res.scalars().first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return {
        "result": "true",
        "user": {
            "id": user.id,
            "name": user.name,
            "followers": [{"id": u.id, "name": u.name} for u in user.followers],
            "following": [{"id": u.id, "name": u.name} for u in user.following],
        },
    }
