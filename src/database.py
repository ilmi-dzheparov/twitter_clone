"""Database configuration and connection utilities."""
import os

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database connection URL, using asyncpg for PostgreSQL
DATABASE_URL = os.getenv(
    "DATABASE_URL"#, "postgresql+asyncpg://twitter_user:twitter_pass@db:5432/twitter_db"
)

# Create an asynchronous engine
async_engine = create_async_engine(DATABASE_URL, echo=True)

# Configure asynchronous session
async_session = sessionmaker(
    bind=async_engine, expire_on_commit=False, class_=AsyncSession
)


async def get_async_db() -> None:
    """Yield an asynchronous database session for use with FastAPI dependency injection."""
    async with async_session() as session:
        yield session


# Declarative base for ORM models
Base = declarative_base()


async def init_db() -> None:
    """
    Initialize the database.

    - Create all tables defined in the ORM models
    - Populate the database with sample users if no users exist
    """
    # Create all tables defined in the models
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Add test users (if the table is empty)
    async with async_session() as session:
        from .models import User

        result = await session.execute(
            select(User).limit(1)  # Check if any users exist
        )
        user = result.scalars().first()
        if not user:
            # Prepopulate with sample users
            users = [
                User(
                    name="ilmi",
                    api_key="test",
                    display_name="Ilmi",
                    avatar_url="https://i.pravatar.cc/150?u=ilmi",
                ),
                User(
                    name="petya",
                    api_key="petya123",
                    display_name="Petya",
                    avatar_url="https://i.pravatar.cc/150?u=petya",
                ),
                User(
                    name="masha",
                    api_key="masha456",
                    display_name="Masha",
                    avatar_url="https://i.pravatar.cc/150?u=masha",
                ),
            ]
            session.add_all(users)
            await session.commit()
