"""Browser interaction actions for Morrow."""

from playwright.async_api import Page


class BrowserActions:
    """High-level browser actions for a session page."""

    def __init__(self, page: Page) -> None:
        """Create actions bound to a browser page."""
        self.page = page

    async def click(self, selector: str) -> None:
        """Click an element by selector."""
        await self.page.click(selector)

    async def type(self, selector: str, text: str) -> None:
        """Type text into an input field."""
        await self.page.fill(selector, text)

    async def screenshot(self) -> bytes:
        """Capture a screenshot of the current page."""
        return await self.page.screenshot()
