import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.database import Base
from src.models import Like, Media, Tweet, User

DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine_test = create_async_engine(DATABASE_URL)
TestSessionLocal = async_sessionmaker(
    bind=engine_test, class_=AsyncSession, expire_on_commit=False
)


"""
Эта фикстура создаёт таблицы в базе один раз за сессию.

await conn.run_sync(Base.metadata.create_all) — создаёт таблицы на основе всех моделей.

После завершения всех тестов: await engine_test.dispose() закрывает соединение.
"""


@pytest_asyncio.fixture(scope="session")
async def async_engine():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine_test
    await engine_test.dispose()


"""
Создаёт новую сессию перед каждым тестом (scope="function").

После выполнения теста делает rollback, чтобы откатить изменения в БД (очистка).
"""


@pytest_asyncio.fixture(scope="function")
async def async_session(async_engine):
    async_session_local = async_sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session_local() as session:
        yield session
        await session.rollback()


"""
Добавляет тестового пользователя в базу перед каждым тестом.

add() → commit() → refresh() — стандартная процедура, чтобы получить актуальный user.id.

Возвращает готового пользователя для использования в тестах 
(например, для авторизации по API key).
"""


@pytest_asyncio.fixture
async def test_user(async_session: AsyncSession):
    user = User(name="testuser", api_key="testkey123")
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_tweet_with_likes(async_session, test_user):
    # Другой пользователь (лайкающий)
    liker = User(name="liker", api_key="liker123")
    async_session.add(liker)
    await async_session.commit()
    await async_session.refresh(liker)

    # Твит
    tweet1 = Tweet(
        content="Тест 1 твит с вложениями", media_ids="[1, 2]", author_id=test_user.id
    )
    tweet2 = Tweet(
        content="Тест 2 твит с вложениями", media_ids="[3, 4]", author_id=test_user.id
    )
    tweet3 = Tweet(
        content="Тест 3 твит с вложениями", media_ids="[5]", author_id=liker.id
    )
    async_session.add_all([tweet1, tweet2, tweet3])
    await async_session.commit()
    await async_session.refresh(tweet1)
    await async_session.refresh(tweet2)
    await async_session.refresh(tweet3)

    # Лайки
    like1 = Like(tweet_id=tweet1.id, user_id=liker.id)
    like2 = Like(tweet_id=tweet1.id, user_id=test_user.id)
    async_session.add_all([like1, like2])
    await async_session.commit()

    # links
    link1 = Media(filename="image1.jpg", user_id=test_user.id)
    link2 = Media(filename="image2.jpg", user_id=test_user.id)
    link3 = Media(filename="image3.jpg", user_id=test_user.id)
    link4 = Media(filename="image4.jpg", user_id=test_user.id)
    link5 = Media(filename="image5.jpg", user_id=liker.id)
    async_session.add_all([link1, link2, link3, link4, link5])
    await async_session.commit()

    return link5


@pytest_asyncio.fixture(autouse=True, scope="function")
async def recreate_db(async_engine: AsyncEngine):
    # Удаляем все таблицы
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    # Создаем таблицы заново
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield
    # Можно ничего не делать после теста, база уже чиста для следующего
