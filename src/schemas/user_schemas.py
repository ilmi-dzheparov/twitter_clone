from pydantic import BaseModel, Field
from typing import Optional, List, Literal


class UserPreview(BaseModel):
    """
    A simplified preview of a user, typically used in lists.
    """
    id: int = Field(..., description="Unique ID of the user")
    name: str = Field(..., description="Name of the user")


class UserProfile(BaseModel):
    """
    Full profile of a user including followers and following lists.
    """
    id: int = Field(..., description="Unique ID of the user")
    name: str = Field(..., description="Name of the user")
    followers: List[UserPreview] = Field(..., description="List of users who follow this user")
    following: List[UserPreview] = Field(..., description="List of users this user is following")


class UserProfileResponse(BaseModel):
    """
    Response schema for a user's profile data.
    """
    result: Literal[True] = Field(..., description="Always True if the profile was retrieved successfully")
    user: UserProfile = Field(..., description="Full profile data of the user")


class UserPostFollow(BaseModel):
    """
    Response schema after following a user.
    """
    result: Literal[True] = Field(..., description="True if the follow action was successful")


class UserDeleteFollow(BaseModel):
    """
    Response schema after unfollowing a user.
    """
    result: Literal[True] = Field(..., description="True if the unfollow action was successful")
