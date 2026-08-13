"""Morrow application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from playwright.async_api import async_playwright

from backend.browser.manager import BrowserSessionManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start and stop Morrow's shared Playwright runtime."""
    async with async_playwright() as playwright:
        app.state.session_manager = BrowserSessionManager(playwright)
        yield

        # Active sessions should be closed before Playwright shuts down.
        for session in list(app.state.session_manager._sessions.values()):
            await session.close()


app = FastAPI(
    title="Morrow",
    description="Private, local-first browser infrastructure.",
    version="0.1.0",
    lifespan=lifespan,
)
