"""Playwright browser launching for Morrow."""

from playwright.async_api import Browser, Playwright


async def launch_browser(playwright: Playwright) -> Browser:
    """Launch a Chromium browser using Morrow's default configuration."""
    return await playwright.chromium.launch(headless=True)
