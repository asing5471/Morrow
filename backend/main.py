"""Morrow FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.api.actions import router as actions_router
from backend.api.sessions import router as sessions_router
from backend.config import settings
from backend.runtime import start_runtime, stop_runtime


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown resources."""
    await start_runtime(app)

    yield

    await stop_runtime(app)


app = FastAPI(
    title="Morrow",
    description="Private, local-first browser infrastructure for browser automation and agents.",
    lifespan=lifespan,
)


app.include_router(sessions_router)
app.include_router(actions_router)


@app.get("/")
async def health_check() -> dict[str, str]:
    """Return basic application status."""
    return {
        "name": "Morrow",
        "status": "running",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host=settings.server.host,
        port=settings.server.port,
        reload=False,
    )
