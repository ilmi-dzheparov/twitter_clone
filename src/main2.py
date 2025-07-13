import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Добро пожаловать в API!"}


@app.get("/api/users/me")
async def get_users_me():
    return JSONResponse({
        "result": "true",
        "user": {
            "id": 1,
            "name": "Ilmi",
            "followers": [],
            "following": [],
        },
    })


if __name__ == "__main__":
    uvicorn.run("src.main:src", host="0.0.0.0", port=8000)