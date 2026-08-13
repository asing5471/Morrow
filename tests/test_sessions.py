"""Tests for Morrow browser session management."""

from backend.browser.manager import BrowserSessionManager


def test_create_session() -> None:
    """A new session should be created and tracked by the manager."""
    manager = BrowserSessionManager()

    session = manager.create_session()

    assert session.id
    assert manager.get_session(session.id) is session


def test_session_ids_are_unique() -> None:
    """Each newly created session should receive a unique ID."""
    manager = BrowserSessionManager()

    first = manager.create_session()
    second = manager.create_session()

    assert first.id != second.id


def test_remove_session() -> None:
    """Removing a session should stop the manager from tracking it."""
    manager = BrowserSessionManager()

    session = manager.create_session()
    removed = manager.remove_session(session.id)

    assert removed is session
    assert manager.get_session(session.id) is None


def test_remove_missing_session() -> None:
    """Removing an unknown session should return None."""
    manager = BrowserSessionManager()

    removed = manager.remove_session("does-not-exist")

    assert removed is None
