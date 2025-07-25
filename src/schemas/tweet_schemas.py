"""Pydantic schemas for the Tweet block."""

from typing import Literal

from pydantic import BaseModel, Field

from src.schemas.user_schemas import UserPreview


class TweetCreateRequest(BaseModel):
    """Request schema for creating a tweet."""

    tweet_data: str = Field(
        ...,
        description="Text content of the tweet",
        example="The weather is great today",
    )
    tweet_media_ids: list[int] | None = Field(
        None,
        description="List of media file IDs attached to the tweet",
        example=[1, 2],
    )


class TweetCreateResponse(BaseModel):
    """Response returned after a successful tweet creation."""

    result: Literal[True] = Field(
        ...,
        description="Indicates whether the tweet was successfully created",
        example=True,
    )
    tweet_id: int = Field(..., description="ID of the newly created tweet", example=12)


class LikeResponse(BaseModel):
    """Schema representing a user who liked a tweet."""

    user_id: int = Field(..., description="ID of the user who liked the tweet")
    name: str = Field(..., description="Name of the user who liked the tweet")


class TweetResponse(BaseModel):
    """Full tweet response with metadata."""

    id: int = Field(..., description="Tweet ID")
    content: str = Field(..., description="Text content of the tweet")
    attachments: list[str] = Field(
        default_factory=list, description="List of media file paths or URLs"
    )
    author: UserPreview = Field(
        ..., description="Preview information of the tweet's author"
    )
    likes: list[LikeResponse] = Field(
        default_factory=list, description="List of users who liked the tweet"
    )


class TweetsGetResponse(BaseModel):
    """Response schema for multiple tweets."""

    result: bool = Field(
        default=True, description="Always true if request is successful"
    )
    tweets: list[TweetResponse] = Field(..., description="List of retrieved tweets")


class TweetDelete(BaseModel):
    """Response schema when a tweet is deleted."""

    result: Literal[True] = Field(
        ..., description="Always true if deletion was successful"
    )


class ErrorResponse(BaseModel):
    """Generic error response schema."""

    result: bool = Field(default=False, description="Always false when an error occurs")
    error_type: str = Field(..., description="Type or category of the error")
    error_message: str = Field(..., description="Detailed error message")


class TweetPostLikeResponse(BaseModel):
    """Response after liking a tweet."""

    result: Literal[True] = Field(
        ..., description="True if like was successfully added"
    )


# Response after removing a like from a tweet
class TweetDeleteLikeResponse(BaseModel):
    """Response after removing a like from a tweet."""

    result: Literal[True] = Field(
        ..., description="True if like was successfully deleted"
    )


class MediaUploadResponse(BaseModel):
    """Response schema for media upload."""

    result: Literal[True] = Field(
        ..., description="Always true if media upload was successful"
    )
    media_id: int = Field(..., description="ID of the uploaded media file")
