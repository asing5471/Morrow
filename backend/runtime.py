"""Morrow runtime lifecycle management."""

from playwright.async_api import async_playwright

from backend.browser.manager import BrowserSessionManager


async def start_runtime(app) -> None:
    """Initialize Morrow runtime resources."""
    app.state.playwright_context = async_playwright()

    app.state.playwright = await app.state.playwright_context.start()

    app.state.session_manager = BrowserSessionManager(
        app.state.playwright,
    )


async def stop_runtime(app) -> None:
    """Shutdown Morrow runtime resources."""
    await app.state.session_manager.close_all()

    await app.state.playwright_context.stop()
