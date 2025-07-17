"""Media upload and handling routes for the Twitter clone API."""

import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, Header, UploadFile

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_db
from src.models import Media, User
from src.schemas.tweet_schemas import MediaUploadResponse

router = APIRouter(prefix="/api/medias", tags=["Medias"])

MEDIA_FOLDER = "/media"


@router.post("", response_model=MediaUploadResponse)
async def upload_media(
    file: UploadFile = File(...),
    api_key: str = Header(..., alias="api-key"),
    db: AsyncSession = Depends(get_async_db),
) -> MediaUploadResponse:
    """
    Upload a JPEG image file and store it in the media directory.

    Associates the uploaded media with the authenticated user.
    Args:
        file (UploadFile): The uploaded image file (must be .jpg).
        api_key (str): The user's API key passed via request headers.
        db (AsyncSession): The asynchronous database session.

    Returns:
        dict: Contains the result flag and the ID of the created media record.
    """
    # Validate API key and retrieve user
    result = await db.execute(select(User).where(User.api_key == api_key))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Validate file extension
    if not file.filename.lower().endswith(".jpg"):
        raise HTTPException(status_code=400, detail="Only .jpg files are allowed")

    # Validate MIME type
    if file.content_type not in ("image/jpeg",):
        raise HTTPException(status_code=400, detail="Invalid file type")

    # Read file contents
    contents = await file.read()

    # Save file to media folder
    os.makedirs(MEDIA_FOLDER, exist_ok=True)
    filename = f"{uuid.uuid4().hex}.jpg"
    filepath = os.path.join(MEDIA_FOLDER, filename)

    with open(filepath, "wb") as f:
        f.write(contents)

    # Store media record in the database
    media = Media(user_id=user.id, filename=filename)
    db.add(media)
    await db.commit()
    await db.refresh(media)

    return {"result": True, "media_id": media.id}
