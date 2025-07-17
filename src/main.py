"""Main entry point for the FastAPI Twitter clone application."""

from fastapi import FastAPI

import uvicorn

from .database import init_db
from .routes import medias, tweets, users


# Create FastAPI application instance
app = FastAPI(title="Microblog API")


@app.on_event("startup")
async def startup() -> None:
    """Event handler that runs at application startup.

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
