from fastapi import APIRouter, Header, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from models import Tweet, User
from schemas import TweetCreateRequest, TweetCreateResponse
from database import get_db
import json

router = APIRouter(prefix="/api/tweets", tags=["Tweets"])

@router.post("", response_model=TweetCreateResponse)
def create_tweet(
    payload: TweetCreateRequest,
    api_key: str = Header(..., alias="api-key"),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.api_key == api_key).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")

    tweet = Tweet(
        content=payload.tweet_data,
        media_ids=json.dumps(payload.tweet_media_ids or []),
        author_id=user.id
    )
    db.add(tweet)
    db.commit()
    db.refresh(tweet)

    return JSONResponse({"result": True, "tweet_id": tweet.id})