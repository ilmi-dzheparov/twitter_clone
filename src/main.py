from fastapi import FastAPI
from .routes import tweets, users, medias
from .database import init_db, Base, async_engine
import uvicorn

# Создание таблиц
# Base.metadata.create_all(bind=async_engine)

# Инициализация тестового пользователя
# init_db()

# Приложение
app = FastAPI(title="Microblog API")

@app.on_event("startup")
async def startup():
    await init_db()

# # Подключение роутеров
app.include_router(users.router)
app.include_router(tweets.router)
app.include_router(medias.router)


if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000)