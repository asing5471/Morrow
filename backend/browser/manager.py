"""Management of active browser sessions."""

from backend.browser.session import BrowserSession


class BrowserSessionManager:
    """Create, track, and remove active browser sessions."""

    def __init__(self) -> None:
        self._sessions: dict[str, BrowserSession] = {}

    def create_session(self) -> BrowserSession:
        """Create and register a new browser session."""
        session = BrowserSession.create()
        self._sessions[session.id] = session
        return session

    def get_session(self, session_id: str) -> BrowserSession | None:
        """Return an active session, or None if it does not exist."""
        return self._sessions.get(session_id)

    def remove_session(self, session_id: str) -> BrowserSession | None:
        """Remove and return a session, if it exists."""
        return self._sessions.pop(session_id, None)
