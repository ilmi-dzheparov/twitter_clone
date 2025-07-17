import tempfile

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from src.database import get_async_db
from src.main import app
from src.models import Like, Tweet, User, followers_table
from src.routes import medias

# # Подключаем фикстуры
# from tests.conftest import async_session, test_user


"""
В FastAPI, БД-сессия передаётся через Depends(get_async_db).

В тестах мы подменим get_async_db, чтобы использовать фикстуру async_session.
"""


@pytest.mark.asyncio
async def test_create_tweet_success(test_user, async_session):
    async def override_get_db():
        yield async_session

    app.dependency_overrides[get_async_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/api/tweets",
            json={"tweet_data": "Hello world", "tweet_media_ids": []},
            headers={"api-key": test_user.api_key},
        )
    assert response.status_code == 200
    assert response.json()["result"] is True


@pytest.mark.asyncio
async def test_get_tweets_success(async_session, test_user, test_tweet_with_likes):
    async def override_get_db():
        yield async_session

    app.dependency_overrides[get_async_db] = override_get_db

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/tweets", headers={"api-key": test_user.api_key}
        )

    assert response.status_code == 200
    data = response.json()
    assert data["result"] is True
    assert isinstance(data["tweets"], list)
    assert data["tweets"][0]["author"]["name"] == test_user.name
    assert len(data["tweets"][0]["attachments"]) == 2
    assert len(data["tweets"][2]["attachments"]) == 1
    assert (
        data["tweets"][2]["attachments"][0]
        == f"http://localhost/media/{test_tweet_with_likes.filename}"
    )
    assert len(data["tweets"][0]["likes"]) == 2

    # Переопределяем select, чтобы симулировать ошибку
    def broken_select(*args, **kwargs):
        raise AttributeError("Simulated DB failure")


@pytest.mark.asyncio
async def test_get_tweets_failure(async_session, monkeypatch):
    # Подделка select, чтобы оно выбрасывало исключение
    def broken_select(*args, **kwargs):
        raise AttributeError("Mocked select error")

    # Подменяем select в конкретном месте, где его использует get_tweets
    monkeypatch.setattr("src.routes.tweets.select", broken_select)

    async def override_get_db():
        yield async_session

    app.dependency_overrides[get_async_db] = override_get_db

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/tweets", headers={"api-key": "fake_key"})

    assert response.status_code == 200
    data = response.json()

    assert data["result"] is False
    assert data["error_type"] == "AttributeError"
    assert data["error_message"] == "Mocked select error"


@pytest.mark.asyncio
async def test_upload_media_success(async_session, test_user, test_tweet_with_likes):
    # Создаём временную директорию
    with tempfile.TemporaryDirectory() as temp_dir:
        # Переопределяем путь к папке медиа
        medias.MEDIA_FOLDER = temp_dir

        async def override_get_db():
            yield async_session

        app.dependency_overrides[get_async_db] = override_get_db

        transport = ASGITransport(app=app)
        file_content = b"test image content"
        files = {"file": ("image.jpg", file_content, "image/jpeg")}

        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/medias", headers={"api-key": test_user.api_key}, files=files
            )

        assert response.status_code == 200
        data = response.json()
        assert data["result"] is True
        assert isinstance(data["media_id"], int)


@pytest.mark.asyncio
async def test_delete_own_tweet(async_session, test_user, test_tweet_with_likes):
    async def override_get_db():
        yield async_session

    app.dependency_overrides[get_async_db] = override_get_db

    # Создаём новый твит, который мы будем удалять
    tweet = Tweet(content="Тест на удаление", author_id=test_user.id)
    async_session.add(tweet)
    await async_session.commit()
    await async_session.refresh(tweet)

    tweet_id = tweet.id

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.delete(
            f"/api/tweets/{tweet_id}", headers={"api-key": test_user.api_key}
        )

    assert response.status_code == 200
    assert response.json() == {"result": True}

    # Проверяем, что твит действительно удалён из базы
    deleted = await async_session.get(Tweet, tweet_id)
    assert deleted is None


@pytest.mark.asyncio
async def test_post_and_delete_like(async_session, test_user, test_tweet_with_likes):
    async def override_get_db():
        yield async_session

    app.dependency_overrides[get_async_db] = override_get_db

    # Создаём новый твит, который мы будем удалять
    tweet = Tweet(content="Tweet without like", author_id=test_user.id)
    async_session.add(tweet)
    await async_session.commit()
    await async_session.refresh(tweet)

    tweet_id = tweet.id

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            f"/api/tweets/{tweet_id}/likes", headers={"api-key": test_user.api_key}
        )

    assert response.status_code == 200
    assert response.json() == {"result": True}

    like = await async_session.execute(
        select(Like).where(Like.user_id == test_user.id, Like.tweet_id == tweet_id)
    )
    assert like.scalar_one_or_none() is not None

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.delete(
            f"/api/tweets/{tweet_id}/likes", headers={"api-key": test_user.api_key}
        )

    assert response.status_code == 200
    assert response.json() == {"result": True}

    like = await async_session.execute(
        select(Like).where(Like.user_id == test_user.id, Like.tweet_id == tweet_id)
    )
    assert like.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_post_and_delete_follow(async_session, test_user, test_tweet_with_likes):
    async def override_get_db():
        yield async_session

    app.dependency_overrides[get_async_db] = override_get_db

    # Creating of user to follow
    followee_user = User(name="followee", api_key="followee_key")
    async_session.add(followee_user)
    await async_session.commit()
    await async_session.refresh(followee_user)

    followee_user_id = followee_user.id

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            f"/api/users/{followee_user_id}/follow",
            headers={"api-key": test_user.api_key},
        )

    assert response.status_code == 200
    assert response.json() == {"result": True}

    # Проверяем наличие follow в базе
    follow = await async_session.execute(
        select(followers_table).where(
            followers_table.c.follower_id == test_user.id,
            followers_table.c.followee_id == followee_user.id,
        )
    )
    assert follow.first() is not None

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.delete(
            f"/api/users/{followee_user_id}/follow",
            headers={"api-key": test_user.api_key},
        )

        assert response.status_code == 200
        assert response.json() == {"result": True}

        # Проверяем follow в базе
        follow = await async_session.execute(
            select(followers_table).where(
                followers_table.c.follower_id == test_user.id,
                followers_table.c.followee_id == followee_user.id,
            )
        )
        assert follow.first() is None


@pytest.mark.asyncio
async def test_get_follow(async_session, test_user, test_tweet_with_likes):
    async def override_get_db():
        yield async_session

    app.dependency_overrides[get_async_db] = override_get_db

    # Creating of user to follow
    followee_user_1 = User(name="followee_1", api_key="followee1_key")
    followee_user_2 = User(name="followee_2", api_key="followee2_key")
    async_session.add_all([followee_user_1, followee_user_2])
    await async_session.commit()
    await async_session.refresh(followee_user_1)
    await async_session.refresh(followee_user_2)

    followee_user_1_id = followee_user_1.id
    followee_user_2_id = followee_user_2.id

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        await ac.post(
            f"/api/users/{followee_user_1_id}/follow",
            headers={"api-key": test_user.api_key},
        )
        await ac.post(
            f"/api/users/{followee_user_2_id}/follow",
            headers={"api-key": test_user.api_key},
        )

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        await ac.post(
            f"/api/users/{test_user.id}/follow",
            headers={"api-key": followee_user_1.api_key},
        )

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/users/me", headers={"api-key": test_user.api_key})

    assert response.status_code == 200
    data = response.json()

    assert data["result"] is True
    assert data["user"]["id"] == test_user.id
    assert len(data["user"]["followers"]) == 1
    assert len(data["user"]["following"]) == 2
    assert data["user"]["following"][0]["name"] == followee_user_1.name
    assert data["user"]["following"][1]["name"] == followee_user_2.name

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response_2 = await ac.get(f"/api/users/{followee_user_1_id}")

    assert response_2.status_code == 200
    data_2 = response_2.json()

    assert data_2["result"] is True
    assert data_2["user"]["id"] == followee_user_1.id
    assert len(data_2["user"]["followers"]) == 1
    assert len(data_2["user"]["following"]) == 1
    assert data_2["user"]["following"][0]["name"] == test_user.name
    assert data_2["user"]["followers"][0]["name"] == test_user.name
