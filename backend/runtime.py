"""Morrow runtime lifecycle management."""

from playwright.async_api import async_playwright

from backend.browser.manager import BrowserSessionManager


async def start_runtime(app) -> None:
    """Initialize Morrow runtime resources."""
    playwright = await async_playwright().start()

    app.state.playwright = playwright
    app.state.session_manager = BrowserSessionManager(playwright)


async def stop_runtime(app) -> None:
    """Shutdown Morrow runtime resources."""
    await app.state.session_manager.close_all()

    await app.state.playwright.stop()
