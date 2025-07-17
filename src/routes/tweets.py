"""Tweet-related API routes including create, read, like, and delete operations."""

import json

from fastapi import APIRouter, Depends, HTTPException, Header

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import get_async_db
from src.models import Like, Media, Tweet, User
from src.schemas.tweet_schemas import (
    TweetCreateRequest,
    TweetCreateResponse,
    TweetDelete,
    TweetDeleteLikeResponse,
    TweetPostLikeResponse,
    TweetsGetResponse,
)

from starlette.responses import JSONResponse

router = APIRouter(prefix="/api/tweets", tags=["Tweets"])


@router.post("", response_model=TweetCreateResponse)
async def create_tweet(
    payload: TweetCreateRequest,
    api_key: str = Header(..., alias="api-key"),
    db: AsyncSession = Depends(get_async_db),
) -> TweetCreateResponse:
    """
    Create a new tweet.

    Args:
        payload: Tweet content and optional media IDs.
        api_key: User API key from request header.
        db: Async database session.

    Returns:
        JSON response containing the result and tweet ID.
    """
    # Get user by API key
    result = await db.execute(select(User).where(User.api_key == api_key))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Create the tweet
    tweet = Tweet(
        content=payload.tweet_data,
        media_ids=json.dumps(payload.tweet_media_ids or []),
        author_id=user.id,
    )
    db.add(tweet)
    await db.commit()
    await db.refresh(tweet)

    return {"result": True, "tweet_id": tweet.id}


@router.get("", response_model=TweetsGetResponse)
async def get_tweets(
        db: AsyncSession = Depends(get_async_db)
) -> TweetsGetResponse:
    """
    Retrieve all tweets with authors, likes, and media attachments.

    Args:
        db: Async database session.

    Returns:
        JSON response with a list of tweets or error details.
    """
    try:
        result = await db.execute(
            select(Tweet).options(
                selectinload(Tweet.user),  # load author
                selectinload(Tweet.likes).selectinload(
                    Like.user
                ),  # load likes and users
            )
        )
        tweets_ = result.scalars().all()

        tweets_list = []
        for item in tweets_:
            # Parse media ID list from JSON string
            media_id_list = json.loads(item.media_ids or "[]")

            # Fetch media filenames from IDs
            media_res = await db.execute(
                select(Media.filename).where(Media.id.in_(media_id_list))
            )
            media_list = media_res.scalars().all()

            # Construct tweet data
            tweet_data = {
                "id": item.id,
                "content": item.content,
                "author": {"id": item.author_id, "name": item.user.name},
                "attachments": [
                    f"http://localhost/media/{filename}" for filename in media_list
                ],
                "likes": [
                    {"user_id": like.user.id, "name": like.user.name}
                    for like in item.likes
                ],
            }
            tweets_list.append(tweet_data)

        return {"result": True, "tweets": tweets_list}

    except SQLAlchemyError as e:
        # Database error
        return JSONResponse(
            {"result": False, "error_type": "DatabaseError", "error_message": str(e)}
        )

    except Exception as e:
        # Any other error
        return JSONResponse(
            {
                "result": False,
                "error_type": e.__class__.__name__,
                "error_message": str(e),
            }
        )


@router.delete("/{id}", response_model=TweetDelete)
async def delete_tweet(
    id: int,
    api_key: str = Header(..., alias="api-key"),
    db: AsyncSession = Depends(get_async_db),
) -> TweetDelete:
    """
    Delete a tweet by ID if it belongs to the user.

    Args:
        id: Tweet ID.
        api_key: User API key from request header.
        db: Async database session.

    Returns:
        JSON response indicating success.
    """
    result = await db.execute(select(User).where(User.api_key == api_key))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")

    tweet_result = await db.execute(
        select(Tweet).where(Tweet.author_id == user.id, Tweet.id == id)
    )
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
    db: AsyncSession = Depends(get_async_db),
) -> TweetPostLikeResponse:
    """
    Like a tweet by ID.

    Args:
        id: Tweet ID.
        api_key: User API key from request header.
        db: Async database session.

    Returns:
        JSON response indicating success.
    """
    result = await db.execute(select(User).where(User.api_key == api_key))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")

    tweet_result = await db.execute(select(Tweet).where(Tweet.id == id))
    if not tweet_result.scalars().first():
        raise HTTPException(status_code=404, detail="Tweet not found")

    like = Like(user_id=user.id, tweet_id=id)
    db.add(like)
    await db.commit()
    await db.refresh(like)

    return {"result": True}


@router.delete("/{id}/likes", response_model=TweetDeleteLikeResponse)
async def delete_like(
    id: int,
    api_key: str = Header(..., alias="api-key"),
    db: AsyncSession = Depends(get_async_db),
) -> TweetDeleteLikeResponse:
    """
    Remove like from a tweet.

    Args:
        id: Tweet ID.
        api_key: User API key from request header.
        db: Async database session.

    Returns:
        JSON response indicating success or error.
    """
    result = await db.execute(select(User).where(User.api_key == api_key))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")

    tweet_result = await db.execute(select(Tweet).where(Tweet.id == id))
    if not tweet_result.scalars().first():
        raise HTTPException(status_code=404, detail="Tweet not found")

    like_result = await db.execute(
        select(Like).where(Like.user_id == user.id, Like.tweet_id == id)
    )
    like = like_result.scalars().first()
    if not like:
        raise HTTPException(status_code=404, detail="Like not found")

    await db.delete(like)
    await db.commit()

    return {"result": True}
