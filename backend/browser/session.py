"""Browser session lifecycle for Morrow."""

from dataclasses import dataclass, field
from uuid import uuid4

from playwright.async_api import Browser, BrowserContext, Page, Playwright


@dataclass
class BrowserSession:
    """Represents one active browser session and its Playwright resources."""

    id: str
    playwright: Playwright
    browser: Browser
    context: BrowserContext
    page: Page
    _closed: bool = field(default=False, init=False)

    @classmethod
    async def create(cls, playwright: Playwright) -> "BrowserSession":
        """Launch a Chromium browser and create an isolated session."""
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        return cls(
            id=str(uuid4()),
            playwright=playwright,
            browser=browser,
            context=context,
            page=page,
        )

    async def navigate(self, url: str) -> None:
        """Navigate the session's page to the given URL."""
        await self.page.goto(url)

    async def close(self) -> None:
        """Close the browser resources owned by this session."""
        if self._closed:
            return

        self._closed = True
        await self.context.close()
        await self.browser.close()
