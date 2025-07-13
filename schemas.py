from pydantic import BaseModel, Field
from typing import Optional, List


class TweetCreateRequest(BaseModel):
    tweet_data: str = Field(..., example="Сегодня хорошая погода")
    tweet_media_ids: Optional[List[int]] = Field(None, example=[1, 2])


class TweetCreateResponse(BaseModel):
    result: bool
    tweet_id: int


class UserPreview(BaseModel):
    id: int
    name: str


class UserProfile(BaseModel):
    id: int
    name: str
    followers: List[UserPreview]
    following: List[UserPreview]


class UserProfileResponse(BaseModel):
    result: str
    user: UserProfile
