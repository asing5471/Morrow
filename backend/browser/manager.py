"""Management of active browser sessions."""

from playwright.async_api import Playwright

from backend.browser.session import BrowserSession


class BrowserSessionManager:
    """Create, track, and remove active browser sessions."""

    def __init__(self, playwright: Playwright) -> None:
        self._playwright = playwright
        self._sessions: dict[str, BrowserSession] = {}

    async def create_session(self) -> BrowserSession:
        """Create and register a new browser session."""
        session = await BrowserSession.create(self._playwright)
        self._sessions[session.id] = session
        return session

    def get_session(self, session_id: str) -> BrowserSession | None:
        """Return an active session, or None if it does not exist."""
        return self._sessions.get(session_id)

    async def remove_session(self, session_id: str) -> BrowserSession | None:
        """Close and remove a session, if it exists."""
        session = self._sessions.pop(session_id, None)

        if session is None:
            return None

        await session.close()
        return session
