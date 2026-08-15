"""Tests for Morrow browser actions."""

from fastapi.testclient import TestClient

from backend.main import app


def test_api_find_element() -> None:
    """The API should find an element matching a CSS selector."""
    with TestClient(app) as client:
        create_response = client.post("/sessions")

        assert create_response.status_code == 201

        session_id = create_response.json()["id"]

        navigate_response = client.post(
            f"/sessions/{session_id}/navigate",
            json={"url": "https://example.com"},
        )

        assert navigate_response.status_code == 200

        response = client.get(
            f"/sessions/{session_id}/element",
            params={"selector": "h1"},
        )

        assert response.status_code == 200
        assert response.json() == {
            "id": session_id,
            "selector": "h1",
            "found": True,
        }


def test_api_find_element_missing() -> None:
    """The API should report when an element does not exist."""
    with TestClient(app) as client:
        create_response = client.post("/sessions")

        assert create_response.status_code == 201

        session_id = create_response.json()["id"]

        response = client.get(
            f"/sessions/{session_id}/element",
            params={"selector": "#does-not-exist"},
        )

        assert response.status_code == 200
        assert response.json() == {
            "id": session_id,
            "selector": "#does-not-exist",
            "found": False,
        }


def test_api_find_element_missing_session() -> None:
    """The API should return 404 for an unknown session."""
    with TestClient(app) as client:
        response = client.get(
            "/sessions/does-not-exist/element",
            params={"selector": "h1"},
        )

        assert response.status_code == 404
        assert response.json() == {
            "detail": "Session not found",
        }


def test_api_click_element() -> None:
    """The API should click an element in the browser session."""
    with TestClient(app) as client:
        create_response = client.post("/sessions")

        assert create_response.status_code == 201

        session_id = create_response.json()["id"]

        navigate_response = client.post(
            f"/sessions/{session_id}/navigate",
            json={"url": "https://example.com"},
        )

        assert navigate_response.status_code == 200

        response = client.post(
            f"/sessions/{session_id}/click",
            json={"selector": "h1"},
        )

        assert response.status_code == 200
        assert response.json() == {
            "id": session_id,
            "status": "clicked",
            "selector": "h1",
        }


def test_api_click_element_missing_session() -> None:
    """The API should return 404 when clicking in an unknown session."""
    with TestClient(app) as client:
        response = client.post(
            "/sessions/does-not-exist/click",
            json={"selector": "button"},
        )

        assert response.status_code == 404
        assert response.json() == {
            "detail": "Session not found",
        }


def test_api_click_element_invalid_selector() -> None:
    """The API should return 400 when a selector cannot be clicked."""
    with TestClient(app) as client:
        create_response = client.post("/sessions")

        assert create_response.status_code == 201

        session_id = create_response.json()["id"]

        response = client.post(
            f"/sessions/{session_id}/click",
            json={"selector": "#does-not-exist"},
        )

        assert response.status_code == 400
        assert response.json() == {
            "detail": "Unable to click element",
        }


def test_api_type_text() -> None:
    """The API should type text into an input element."""
    with TestClient(app) as client:
        create_response = client.post("/sessions")

        assert create_response.status_code == 201

        session_id = create_response.json()["id"]

        response = client.post(
            f"/sessions/{session_id}/navigate",
            json={"url": "data:text/html,<input id='name'>"},
        )

        assert response.status_code == 400

        # The navigation security layer intentionally blocks data URLs.
        # Use a page created through the browser session instead.
        manager = client.app.state.session_manager
        session = manager.get_session(session_id)

        assert session is not None

        import asyncio

        asyncio.run(
            session.page.set_content(
                "<html><body><input id='name'></body></html>"
            )
        )

        response = client.post(
            f"/sessions/{session_id}/type",
            json={
                "selector": "#name",
                "text": "Morrow",
            },
        )

        assert response.status_code == 200
        assert response.json() == {
            "id": session_id,
            "status": "typed",
            "selector": "#name",
        }


def test_api_type_text_missing_session() -> None:
    """The API should return 404 when typing in an unknown session."""
    with TestClient(app) as client:
        response = client.post(
            "/sessions/does-not-exist/type",
            json={
                "selector": "#name",
                "text": "Morrow",
            },
        )

        assert response.status_code == 404
        assert response.json() == {
            "detail": "Session not found",
        }
