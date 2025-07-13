import os

from sqlalchemy import select, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLALCHEMY_DATABASE_URL = "sqlite:///./microblog.db"
#
# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL,
#     connect_args={"check_same_thread": False}, echo=True
# )

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://twitter_user:twitter_pass@db:5432/twitter_db")

# engine = create_engine(DATABASE_URL)

async_engine = create_async_engine(DATABASE_URL, echo=True)

async_session = sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    class_=AsyncSession
)

async def get_async_db():
    async with async_session() as session:
        yield session

# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Асинхронная инициализация БД (создание таблиц)
async def init_db():
    # Создаём таблицы
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print(Base.metadata.tables.keys())

    # Добавление тестов
    # ых пользователей — тоже асинхронно
    async with async_session() as session:
        from .models import User
        result = await session.execute(
            # Проверка, есть ли пользователи
            # SQLAlchemy 2.0 синтаксис:
            select(User).limit(1)
        )
        user = result.scalars().first()
        if not user:
            users = [
                User(name="ilmi", api_key="test", display_name="Ilmi",
                     avatar_url="https://i.pravatar.cc/150?u=ilmi"),
                User(name="petya", api_key="petya123", display_name="Petya",
                     avatar_url="https://i.pravatar.cc/150?u=petya"),
                User(name="masha", api_key="masha456", display_name="Masha",
                     avatar_url="https://i.pravatar.cc/150?u=masha"),
            ]
            session.add_all(users)
            await session.commit()

# def init_db():
#     db = SessionLocal()
#     from .models import User
#
#     # Создание таблиц (если они еще не существуют)
#     Base.metadata.create_all(bind=engine)
#
#     try:
#         # проверим наличие тестового пользователя
#         # user = db.query(User).filter(User.api_key == "test").first()
#         if not db.query(User).first():
#             users = [
#                 User(name="ilmi", api_key="test", display_name="Ilmi",
#                      avatar_url="https://i.pravatar.cc/150?u=ilmi"),
#                 User(name="petya", api_key="petya123", display_name="Petya",
#                      avatar_url="https://i.pravatar.cc/150?u=petya"),
#                 User(name="masha", api_key="masha456", display_name="Masha",
#                      avatar_url="https://i.pravatar.cc/150?u=masha"),
#             ]
#             db.add_all(users)
#             db.commit()
#     finally:
#         db.close()


# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()