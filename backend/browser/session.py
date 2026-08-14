"""Browser session lifecycle for Morrow."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4

from playwright.async_api import Browser, BrowserContext, Page, Playwright

from backend.browser.playwright import launch_browser
from backend.config import settings
from backend.security.network import is_safe_navigation_url


@dataclass
class BrowserSession:
    """Represents one active browser session and its Playwright resources."""

    id: str
    playwright: Playwright
    browser: Browser
    context: BrowserContext
    page: Page
    created_at: datetime
    status: str = "active"
    _closed: bool = field(default=False, init=False)

    @classmethod
    async def create(cls, playwright: Playwright) -> "BrowserSession":
        """Launch a Chromium browser and create an isolated session."""
        browser = await launch_browser(playwright, settings.browser)
        context = await browser.new_context()
        page = await context.new_page()

        return cls(
            id=str(uuid4()),
            playwright=playwright,
            browser=browser,
            context=context,
            page=page,
            created_at=datetime.now(UTC),
        )

    @property
    def current_url(self) -> str:
        """Return the current browser page URL."""
        return self.page.url

    async def navigate(self, url: str) -> None:
        """Navigate the session's page to an allowed web URL."""
        if not await is_safe_navigation_url(url):
            raise ValueError("Invalid navigation URL")

        await self.page.goto(url)

    async def title(self) -> str:
        """Return the current page title."""
        return await self.page.title()

    async def click(self, selector: str) -> None:
        """Click an element on the page."""
        await self.page.click(selector)

    async def fill(self, selector: str, value: str) -> None:
        """Fill an input element."""
        await self.page.fill(selector, value)

    async def content(self) -> str:
        """Return the current page HTML."""
        return await self.page.content()

    async def close(self) -> None:
        """Close the browser resources owned by this session."""
        if self._closed:
            return

        self._closed = True
        self.status = "closed"

        await self.context.close()
        await self.browser.close()
