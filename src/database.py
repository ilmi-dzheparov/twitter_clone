"""Database configuration and connection utilities."""
import asyncio
import os

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database connection URL, using asyncpg for PostgreSQL
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+asyncpg://twitter_user:twitter_pass@db:5432/twitter_db"
    # "DATABASE_URL", "postgresql+asyncpg://twitter_user:twitter_pass@127.0.0.1:5432/twitter_db"
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
# from . import models

async def init_db() -> None:
    """
    Initialize the database.

    - Create all tables defined in the ORM models
    - Populate the database with sample users if no users exist
    """


    from .models import User
    # Add a retry loop to wait for the database to become available
    # Attempt to connect 10 times with a 3-second delay between attempts
    for i in range(10):
        try:
            async with async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            # If tables are created successfully, attempt to populate with users
            async with async_session() as session:

                result = await session.execute(select(User).limit(1))
                user = result.scalars().first()
                if not user:
                    # Prepopulate with sample users if the table is empty
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
                    print("Database initialized and seeded successfully!")
                    session.add_all(users)
                    await session.commit()
            break
        except OperationalError:
            print(f"Database not ready, attempt {i + 1}/10...")
            await asyncio.sleep(3)
        except Exception as e:
            print(f"An error occurred: {e}")
            break

    # # Create all tables defined in the models
    # async with async_engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)
    #
    # # Add test users (if the table is empty)
    # async with async_session() as session:
    #     from .models import User
    #
    #     result = await session.execute(
    #         select(User).limit(1)  # Check if any users exist
    #     )
    #     user = result.scalars().first()
    #     if not user:
    #         # Prepopulate with sample users
    #         users = [
    #             User(
    #                 name="ilmi",
    #                 api_key="test",
    #                 display_name="Ilmi",
    #                 avatar_url="https://i.pravatar.cc/150?u=ilmi",
    #             ),
    #             User(
    #                 name="petya",
    #                 api_key="petya123",
    #                 display_name="Petya",
    #                 avatar_url="https://i.pravatar.cc/150?u=petya",
    #             ),
    #             User(
    #                 name="masha",
    #                 api_key="masha456",
    #                 display_name="Masha",
    #                 avatar_url="https://i.pravatar.cc/150?u=masha",
    #             ),
    #         ]
    #         session.add_all(users)
    #         await session.commit()