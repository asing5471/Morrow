"""Tests for Morrow browser session management."""

import pytest
from fastapi.testclient import TestClient
from playwright.async_api import async_playwright
from pydantic import ValidationError

from backend.api.schemas import NavigateRequest
from backend.browser.manager import BrowserSessionManager
from backend.main import app
from backend.security import network


@pytest.mark.asyncio
async def test_create_session() -> None:
    """A new session should launch a browser and create a page."""
    async with async_playwright() as playwright:
        manager = BrowserSessionManager(playwright)

        session = await manager.create_session()

        assert session.id
        assert manager.get_session(session.id) is session
        assert session.browser.is_connected()
        assert not session.page.is_closed()
        assert session.status == "active"
        assert session.current_url == "about:blank"
        assert session.created_at is not None

        await manager.close_all()


@pytest.mark.asyncio
async def test_session_ids_are_unique() -> None:
    """Each newly created session should receive a unique ID."""
    async with async_playwright() as playwright:
        manager = BrowserSessionManager(playwright)

        first = await manager.create_session()
        second = await manager.create_session()

        assert first.id != second.id

        await manager.close_all()


@pytest.mark.asyncio
async def test_sessions_are_isolated() -> None:
    """Browser sessions should have independent contexts and pages."""
    async with async_playwright() as playwright:
        manager = BrowserSessionManager(playwright)

        first = await manager.create_session()
        second = await manager.create_session()

        assert first.context is not second.context
        assert first.page is not second.page
        assert first.current_url == "about:blank"
        assert second.current_url == "about:blank"

        await first.navigate("https://example.com")

        assert first.current_url == "https://example.com/"
        assert second.current_url == "about:blank"

        await manager.close_all()


@pytest.mark.asyncio
async def test_remove_session() -> None:
    """Removing a session should close its browser and stop tracking it."""
    async with async_playwright() as playwright:
        manager = BrowserSessionManager(playwright)

        session = await manager.create_session()
        removed = await manager.remove_session(session.id)

        assert removed is session
        assert manager.get_session(session.id) is None
        assert not session.browser.is_connected()
        assert session.status == "closed"

        await manager.close_all()


@pytest.mark.asyncio
async def test_remove_missing_session() -> None:
    """Removing an unknown session should return None."""
    async with async_playwright() as playwright:
        manager = BrowserSessionManager(playwright)

        removed = await manager.remove_session("does-not-exist")

        assert removed is None

        await manager.close_all()


@pytest.mark.asyncio
async def test_navigate() -> None:
    """A session should be able to navigate its page to a URL."""
    async with async_playwright() as playwright:
        manager = BrowserSessionManager(playwright)

        session = await manager.create_session()
        await session.navigate("https://example.com")

        assert session.page.url == "https://example.com/"
        assert session.current_url == "https://example.com/"

        await manager.close_all()


@pytest.mark.asyncio
async def test_page_title() -> None:
    """A session should expose the current page title."""
    async with async_playwright() as playwright:
        manager = BrowserSessionManager(playwright)

        session = await manager.create_session()
        await session.navigate("https://example.com")

        assert await session.page.title() == "Example Domain"

        await manager.close_all()


def test_navigate_request_accepts_url() -> None:
    """Navigate requests should accept a URL string."""
    request = NavigateRequest(url="https://example.com")

    assert request.url == "https://example.com"


def test_navigate_request_requires_url() -> None:
    """Navigate requests should require a URL."""
    with pytest.raises(ValidationError):
        NavigateRequest()


def test_api_create_session() -> None:
    """The API should create a session and return its status."""
    with TestClient(app) as client:
        response = client.post("/sessions")

        assert response.status_code == 201

        body = response.json()

        assert body["id"]
        assert body["status"] == "active"


def test_api_get_session() -> None:
    """The API should return session metadata."""
    with TestClient(app) as client:
        create_response = client.post("/sessions")

        assert create_response.status_code == 201

        session_id = create_response.json()["id"]

        response = client.get(f"/sessions/{session_id}")

        assert response.status_code == 200

        body = response.json()

        assert body["id"] == session_id
        assert body["status"] == "active"
        assert body["created_at"]
        assert body["current_url"] == "about:blank"


def test_api_delete_session() -> None:
    """The API should close and remove an active browser session."""
    with TestClient(app) as client:
        create_response = client.post("/sessions")

        assert create_response.status_code == 201

        session_id = create_response.json()["id"]

        response = client.delete(f"/sessions/{session_id}")

        assert response.status_code == 200
        assert response.json() == {
            "id": session_id,
            "status": "closed",
        }

        missing_response = client.get(f"/sessions/{session_id}")

        assert missing_response.status_code == 404
        assert missing_response.json() == {
            "detail": "Session not found",
        }


def test_api_navigate_session() -> None:
    """The API should navigate an active browser session."""
    with TestClient(app) as client:
        create_response = client.post("/sessions")

        assert create_response.status_code == 201

        session_id = create_response.json()["id"]

        response = client.post(
            f"/sessions/{session_id}/navigate",
            json={"url": "https://example.com"},
        )

        assert response.status_code == 200
        assert response.json() == {
            "id": session_id,
            "status": "navigated",
            "url": "https://example.com/",
        }


def test_api_navigate_missing_session() -> None:
    """The API should return 404 for an unknown session."""
    with TestClient(app) as client:
        response = client.post(
            "/sessions/does-not-exist/navigate",
            json={"url": "https://example.com"},
        )

        assert response.status_code == 404
        assert response.json() == {
            "detail": "Session not found",
        }


def test_api_navigate_rejects_file_url() -> None:
    """The API should reject file URLs."""
    with TestClient(app) as client:
        create_response = client.post("/sessions")

        assert create_response.status_code == 201

        session_id = create_response.json()["id"]

        response = client.post(
            f"/sessions/{session_id}/navigate",
            json={"url": "file:///etc/passwd"},
        )

        assert response.status_code == 400
        assert response.json() == {
            "detail": "Invalid navigation URL",
        }


def test_api_navigate_rejects_javascript_url() -> None:
    """The API should reject JavaScript URLs."""
    with TestClient(app) as client:
        create_response = client.post("/sessions")

        assert create_response.status_code == 201

        session_id = create_response.json()["id"]

        response = client.post(
            f"/sessions/{session_id}/navigate",
            json={"url": "javascript:alert(1)"},
        )

        assert response.status_code == 400
        assert response.json() == {
            "detail": "Invalid navigation URL",
        }


def test_api_navigate_rejects_private_dns(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The API should reject hostnames resolving to private IPs."""

    async def fake_resolve_hostname(hostname: str) -> list[str]:
        return ["127.0.0.1"]

    monkeypatch.setattr(
        network,
        "resolve_hostname",
        fake_resolve_hostname,
    )

    with TestClient(app) as client:
        create_response = client.post("/sessions")

        assert create_response.status_code == 201

        session_id = create_response.json()["id"]

        response = client.post(
            f"/sessions/{session_id}/navigate",
            json={"url": "https://example.com"},
        )

        assert response.status_code == 400
        assert response.json() == {
            "detail": "Invalid navigation URL",
        }


def test_api_shutdown_closes_sessions() -> None:
    """Application shutdown should close active browser sessions."""
    with TestClient(app) as client:
        response = client.post("/sessions")

        assert response.status_code == 201

        session_id = response.json()["id"]

        manager = client.app.state.session_manager
        session = manager.get_session(session_id)

        assert session is not None
        assert session.status == "active"

    assert session.status == "closed"
    assert manager.get_session(session_id) is None

@pytest.mark.asyncio
async def test_max_sessions_limit() -> None:
    """The manager should reject sessions beyond the configured limit."""
    async with async_playwright() as playwright:
        manager = BrowserSessionManager(playwright)

        sessions = []

        for _ in range(5):
            sessions.append(await manager.create_session())

        with pytest.raises(
            RuntimeError,
            match="Maximum number of browser sessions reached",
        ):
            await manager.create_session()

        await manager.close_all()
