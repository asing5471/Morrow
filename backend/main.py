"""Morrow FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from playwright.async_api import async_playwright

from backend.api.sessions import router as sessions_router
from backend.browser.manager import BrowserSessionManager
from backend.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown resources."""
    async with async_playwright() as playwright:
        app.state.session_manager = BrowserSessionManager(playwright)

        yield

        await app.state.session_manager.close_all()


app = FastAPI(
    title="Morrow",
    description="Private, local-first browser infrastructure for browser automation and agents.",
    lifespan=lifespan,
)


app.include_router(sessions_router)


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
