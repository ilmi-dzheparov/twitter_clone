from fastapi import APIRouter, Header, HTTPException, Depends, UploadFile, File
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.models import Tweet, User, Like, Media
from src.schemas.tweet_schemas import (
    TweetCreateRequest,
    TweetCreateResponse,
    TweetsGetResponse,
    TweetDelete,
    TweetPostLikeResponse,
    TweetDeleteLikeResponse,
    MediaUploadResponse,
)
from src.database import get_async_db
import json
import os


router = APIRouter(prefix="/api/tweets", tags=["Tweets"])


@router.post("", response_model=TweetCreateResponse)
async def create_tweet(
    payload: TweetCreateRequest,
    api_key: str = Header(..., alias="api-key"),
    db: AsyncSession = Depends(get_async_db)
):
    # Получаем пользователя по API-ключу
    result = await db.execute(select(User).where(User.api_key == api_key))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Создаём твит
    tweet = Tweet(
        content=payload.tweet_data,
        media_ids=json.dumps(payload.tweet_media_ids or []),
        author_id=user.id
    )
    db.add(tweet)
    await db.commit()
    await db.refresh(tweet)

    # # Привязываем медиа к твиту (если указаны)
    # if payload.tweet_media_ids:
    #     for media_id in payload.tweet_media_ids:
    #         link = Link(
    #             tweet_id=tweet.id,
    #             link_id=media_id
    #         )
    #         db.add(link)
    #     await db.commit()

    return {"result": True, "tweet_id": tweet.id}


@router.get("", response_model=TweetsGetResponse)
async def get_tweets(
    db: AsyncSession = Depends(get_async_db)
):
    try:
        # result = await db.execute(select(User).where(User.api_key == api_key))
        # user = result.scalars().first()
        #
        # if not user:
        #     return {
        #         "result": False,
        #         "error_type": "AuthError",
        #         "error_message": "Invalid API key"
        #     }

        # tweets_res = await db.execute(select(Tweet))
        # tweets_ = tweets_res.scalars().all()
        # tweets_list = []
        # for item in tweets_:
        #     tweet_data = {
        #         "id": item.id,
        #         "content": item.content,
        #         "author": {"id": item.author_id, "name": item.user.name}
        #     }
        #
        #     links_result = await db.execute(select(Link).where(Link.tweet_id == item.id))
        #     tweet_data["attachments"] = [link.id for link in links_result.scalars().all()]
        #
        #     likes_result = await db.execute(select(Like).where(Like.tweet_id == item.id))
        #     likes_ = likes_result.scalars().all()
        #     tweet_data["likes"] = [
        #         {"user_id": like.user.id, "name": like.user.name} for like in likes_
        #     ]
        #
        #     tweets_list.append(tweet_data)

        result = await db.execute(
            select(Tweet)
            .options(
                selectinload(Tweet.user),  # загрузить автора
                # selectinload(Tweet.medias),  # загрузить ссылки
                selectinload(Tweet.likes).selectinload(Like.user)  # загрузить лайки и пользователей, поставивших лайк
            )
        )
        tweets_ = result.scalars().all()

        tweets_list = []
        for item in tweets_:
            # media_ids хранится как JSON-строка -> распарсим
            media_id_list = json.loads(item.media_ids or "[]")

            # Запрашиваем соответствующие Media объекты
            media_res = await db.execute(
                select(Media.filename).where(Media.id.in_(media_id_list))
            )
            media_list = media_res.scalars().all()

            # Формируем данные твита
            tweet_data = {
                "id": item.id,
                "content": item.content,
                "author": {"id": item.author_id, "name": item.user.name},
                "attachments": [f"http://localhost/media/{filename}" for filename in media_list],
                "likes": [{"user_id": like.user.id, "name": like.user.name} for like in item.likes]
            }
            tweets_list.append(tweet_data)

        return {
            "result": True,
            "tweets": tweets_list
        }

    except SQLAlchemyError as e:
        # Ошибка базы данных
        return {
            "result": False,
            "error_type": "DatabaseError",
            "error_message": str(e)
        }

    except Exception as e:
        # Любая другая ошибка
        return {
            "result": False,
            "error_type": e.__class__.__name__,
            "error_message": str(e)
        }


@router.delete("/{id}", response_model=TweetDelete)
async def delete_tweet(
        id: int,
        api_key: str = Header(..., alias="api-key"),
        db: AsyncSession = Depends(get_async_db)
):
    result = await db.execute(select(User).where(User.api_key == api_key))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")

    tweet_result = await db.execute(select(Tweet).where(Tweet.author_id == user.id, Tweet.id == id))
    tweet = tweet_result.scalars().first()
    if not tweet:
        raise HTTPException(status_code=404, detail="Tweet not found")

    await db.delete(tweet)
    await db.commit()

    return {"result": True}


@router.post("/{id}/likes", response_model=TweetPostLikeResponse)
async def create_like(
        id: int,
        api_key: str = Header(..., alias="api-key"),
        db: AsyncSession = Depends(get_async_db)
):
    result = await db.execute(select(User).where(User.api_key == api_key))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")

    tweet_result = await db.execute(select(Tweet).where(Tweet.id == id))
    if not tweet_result.scalars().first():
        raise HTTPException(status_code=404, detail="Tweet not found")

    like = Like(
        user_id=user.id,
        tweet_id=id
    )
    db.add(like)
    await db.commit()
    await db.refresh(like)

    return {"result": True}


@router.delete("/{id}/likes", response_model=TweetDeleteLikeResponse)
async def delete_like(
        id: int,
        api_key: str = Header(..., alias="api-key"),
        db: AsyncSession = Depends(get_async_db)
):
    result = await db.execute(select(User).where(User.api_key == api_key))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")

    tweet_result = await db.execute(select(Tweet).where(Tweet.id == id))
    if not tweet_result.scalars().first():
        raise HTTPException(status_code=404, detail="Tweet not found")

    like_result = await db.execute(select(Like).where(Like.user_id == user.id, Like.tweet_id == id))
    like = like_result.scalars().first()
    if not like:
        raise HTTPException(status_code=404, detail="Like not found")

    await db.delete(like)
    await db.commit()

    return {"result": True}
