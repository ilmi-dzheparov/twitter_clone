from fastapi import FastAPI
from .routes import tweets, users, medias
from .database import init_db, Base, async_engine
import uvicorn

# Create FastAPI application instance
app = FastAPI(title="Microblog API")

@app.on_event("startup")
async def startup():
    """
    Event handler that runs at application startup.
    Initializes the database and creates a test user if needed.
    """
    await init_db()

# Include routers for different parts of the application
app.include_router(users.router)
app.include_router(tweets.router)
app.include_router(medias.router)


if __name__ == "__main__":
    # Run the app using Uvicorn in development mode
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000)