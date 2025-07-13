from pydantic import BaseModel, Field
from typing import Optional, List, Literal


class UserPreview(BaseModel):
    id: int
    name: str


class UserProfile(BaseModel):
    id: int
    name: str
    followers: List[UserPreview]
    following: List[UserPreview]


class UserProfileResponse(BaseModel):
    result: bool = Literal[True]
    user: UserProfile


class UserPostFollow(BaseModel):
    result: bool = Literal[True]


class UserDeleteFollow(BaseModel):
    result: bool = Literal[True]
