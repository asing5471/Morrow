"""Playwright browser launching for Morrow."""

from playwright.async_api import Browser, Playwright

from backend.config import BrowserSettings


async def launch_browser(
    playwright: Playwright,
    settings: BrowserSettings,
) -> Browser:
    """Launch a Chromium browser using Morrow's browser settings."""
    return await playwright.chromium.launch(headless=settings.headless)
