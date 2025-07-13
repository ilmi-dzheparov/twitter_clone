from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import users, tweets
from database import init_db
from database import Base, engine
from starlette.responses import FileResponse
import uvicorn
from pathlib import Path


# Создание таблиц
Base.metadata.create_all(bind=engine)

# Инициализация тестового пользователя
init_db()

# Приложение
app = FastAPI(title="Microblog API")

# # Подключение роутеров
app.include_router(users.router)
app.include_router(tweets.router)


if __name__ == "__main__":
    uvicorn.run("src.main:src", host="0.0.0.0", port=8000)