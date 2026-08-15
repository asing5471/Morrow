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

    async def page_title(self) -> str:
        """Return the current page title."""
        return await self.page.title()

    async def inspect(self) -> dict[str, str]:
        """Return basic information about the current page."""
        return {
            "url": self.current_url,
            "title": await self.page.title(),
            "text": await self.page.locator("body").inner_text(),
        }

    async def find_element(self, selector: str) -> bool:
        """Return whether an element matching the selector exists."""
        locator = self.page.locator(selector)
        return await locator.count() > 0

    async def get_element_text(self, selector: str) -> str:
        """Return the visible text of an element matching the selector."""
        try:
            return await self.page.locator(selector).inner_text()
        except Exception as exc:
            raise ValueError("Unable to get element text") from exc

    async def screenshot(self) -> bytes:
        """Capture the current browser page as a PNG image."""
        return await self.page.screenshot(type="png")

    async def click(self, selector: str) -> None:
        """Click an element matching the selector."""
        try:
            await self.page.locator(selector).click()
        except Exception as exc:
            raise ValueError("Unable to click element") from exc

    async def type_text(self, selector: str, text: str) -> None:
        """Type text into an element matching the selector."""
        try:
            await self.page.locator(selector).fill(text)
        except Exception as exc:
            raise ValueError("Unable to type into element") from exc

    async def hover(self, selector: str) -> None:
        """Hover over an element matching the selector."""
        try:
            await self.page.locator(selector).hover()
        except Exception as exc:
            raise ValueError("Unable to hover over element") from exc

    async def get_cookies(self) -> list[dict]:
        """Return cookies for the current browser context."""
        return await self.context.cookies()

    async def set_cookie(self, cookie: dict) -> None:
        """Add a cookie to the current browser context."""
        await self.context.add_cookies([cookie])

    async def clear_cookies(self) -> None:
        """Clear all cookies from the current browser context."""
        await self.context.clear_cookies()

    async def get_local_storage(self) -> dict[str, str]:
        """Return all local storage values for the current page."""
        return await self.page.evaluate(
            "() => Object.fromEntries(Object.entries(localStorage))"
        )

    async def set_local_storage(self, key: str, value: str) -> None:
        """Set a local storage value for the current page."""
        await self.page.evaluate(
            """([key, value]) => {
                localStorage.setItem(key, value);
            }""",
            [key, value],
        )

    async def clear_local_storage(self) -> None:
        """Clear all local storage for the current page."""
        await self.page.evaluate("() => localStorage.clear()")

    async def navigate(self, url: str) -> None:
        """Navigate the session's page to an allowed web URL."""
        if not await is_safe_navigation_url(url):
            raise ValueError("Invalid navigation URL")

        await self.page.goto(url)

    async def close(self) -> None:
        """Close the browser resources owned by this session."""
        if self._closed:
            return

        self._closed = True
        self.status = "closed"

        await self.context.close()
        await self.browser.close()
