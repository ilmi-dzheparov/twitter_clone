import uuid

from fastapi import APIRouter, Header, HTTPException, Depends, UploadFile, File
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.models import Tweet, User, Like, Media
from src.schemas.tweet_schemas import MediaUploadResponse
from src.database import get_async_db
import os


router = APIRouter(prefix="/api/medias", tags=["Medias"])

MEDIA_FOLDER = "/media"

@router.post("", response_model=MediaUploadResponse)
async def upload_media(
    file: UploadFile = File(...),
    api_key: str = Header(..., alias="api-key"),
    db: AsyncSession = Depends(get_async_db),
):
    # Проверка API-ключа
    result = await db.execute(select(User).where(User.api_key == api_key))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Проверка расширения файла
    if not file.filename.lower().endswith(".jpg"):
        raise HTTPException(status_code=400, detail="Only .jpg files are allowed")

    # Проверка MIME-типа
    if file.content_type not in ("image/jpeg",):
        raise HTTPException(status_code=400, detail="Invalid file type")

    # Читаем содержимое файла
    contents = await file.read()

    # Сохраняем файл в папку media
    os.makedirs(MEDIA_FOLDER, exist_ok=True)
    filename = f"{uuid.uuid4().hex}.jpg"
    filepath = os.path.join(MEDIA_FOLDER, filename)

    with open(filepath, "wb") as f:
        f.write(contents)

    # Сохраняем запись о медиа в базу
    media = Media(user_id=user.id, filename=filename)
    db.add(media)
    await db.commit()
    await db.refresh(media)

    return {"result": True, "media_id": media.id}
