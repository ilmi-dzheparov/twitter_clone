from fastapi import APIRouter, Header, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import UserProfileResponse

router = APIRouter(prefix="/api/users", tags=["Users"])

@router.get("/me", response_model=UserProfileResponse)
def get_me(api_key: str = Header(..., alias="api-key"), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.api_key == api_key).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")

    followers_data = [
        {"id": follower.id, "name": follower.name}
        for follower in user.followers
    ]
    following_data = [
        {"id": followee.id, "name": followee.name}
        for followee in user.following
    ]

    return JSONResponse({
        "result": "true",
        "user": {
            "id": user.id,
            "name": user.name,
            "followers": followers_data,
            "following": following_data,
        },
    })