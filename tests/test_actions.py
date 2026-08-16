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


def test_api_find_element_not_found() -> None:
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
            json={"selector": "h1"},
        )

        assert response.status_code == 404
        assert response.json() == {
            "detail": "Session not found",
        }


def test_api_click_element_invalid_selector() -> None:
    """The API should return 400 when an element cannot be clicked."""
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


def test_api_type_text_invalid_element() -> None:
    """The API should return 400 when typing into a missing element."""
    with TestClient(app) as client:
        create_response = client.post("/sessions")

        assert create_response.status_code == 201
        session_id = create_response.json()["id"]

        response = client.post(
            f"/sessions/{session_id}/type",
            json={
                "selector": "#does-not-exist",
                "text": "Morrow",
            },
        )

        assert response.status_code == 400
        assert response.json() == {
            "detail": "Unable to type into element",
        }


def test_api_get_element_text() -> None:
    """The API should return text for a matching element."""
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
            f"/sessions/{session_id}/element/text",
            params={"selector": "h1"},
        )

        assert response.status_code == 200
        assert response.json() == {
            "id": session_id,
            "selector": "h1",
            "text": "Example Domain",
        }


def test_api_get_element_text_missing_session() -> None:
    """The API should return 404 for an unknown session."""
    with TestClient(app) as client:
        response = client.get(
            "/sessions/does-not-exist/element/text",
            params={"selector": "h1"},
        )

        assert response.status_code == 404
        assert response.json() == {
            "detail": "Session not found",
        }


def test_api_get_element_text_missing_element() -> None:
    """The API should return 400 when the element does not exist."""
    with TestClient(app) as client:
        create_response = client.post("/sessions")

        assert create_response.status_code == 201
        session_id = create_response.json()["id"]

        response = client.get(
            f"/sessions/{session_id}/element/text",
            params={"selector": "#does-not-exist"},
        )

        assert response.status_code == 400
        assert response.json() == {
            "detail": "Unable to get element text",
        }


def test_api_screenshot_session() -> None:
    """The API should return a PNG screenshot of the current page."""
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
            f"/sessions/{session_id}/screenshot",
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"
        assert response.content.startswith(b"\x89PNG\r\n\x1a\n")
        assert len(response.content) > 100


def test_api_screenshot_missing_session() -> None:
    """The API should return 404 for an unknown session."""
    with TestClient(app) as client:
        response = client.get(
            "/sessions/does-not-exist/screenshot",
        )

        assert response.status_code == 404
        assert response.json() == {
            "detail": "Session not found",
        }


def test_api_hover_element() -> None:
    """The API should hover over an element in the browser session."""
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
            f"/sessions/{session_id}/hover",
            json={"selector": "h1"},
        )

        assert response.status_code == 200
        assert response.json() == {
            "id": session_id,
            "status": "hovered",
            "selector": "h1",
        }


def test_api_hover_element_missing_session() -> None:
    """The API should return 404 when hovering in an unknown session."""
    with TestClient(app) as client:
        response = client.post(
            "/sessions/does-not-exist/hover",
            json={"selector": "h1"},
        )

        assert response.status_code == 404
        assert response.json() == {
            "detail": "Session not found",
        }


def test_api_hover_element_invalid_selector() -> None:
    """The API should return 400 when an element cannot be hovered."""
    with TestClient(app) as client:
        create_response = client.post("/sessions")

        assert create_response.status_code == 201
        session_id = create_response.json()["id"]

        response = client.post(
            f"/sessions/{session_id}/hover",
            json={"selector": "#does-not-exist"},
        )

        assert response.status_code == 400
        assert response.json() == {
            "detail": "Unable to hover over element",
        }


def test_api_set_and_get_cookies() -> None:
    """The API should set and return browser cookies."""
    with TestClient(app) as client:
        create_response = client.post("/sessions")

        assert create_response.status_code == 201
        session_id = create_response.json()["id"]

        set_response = client.post(
            f"/sessions/{session_id}/cookies",
            json={
                "name": "morrow_test",
                "value": "hello",
                "url": "https://example.com",
            },
        )

        assert set_response.status_code == 200
        assert set_response.json() == {
            "id": session_id,
            "status": "cookie_set",
            "name": "morrow_test",
        }

        get_response = client.get(
            f"/sessions/{session_id}/cookies",
        )

        assert get_response.status_code == 200

        body = get_response.json()

        assert body["id"] == session_id
        assert any(
            cookie["name"] == "morrow_test"
            and cookie["value"] == "hello"
            for cookie in body["cookies"]
        )


def test_api_clear_cookies() -> None:
    """The API should clear all browser cookies."""
    with TestClient(app) as client:
        create_response = client.post("/sessions")

        assert create_response.status_code == 201
        session_id = create_response.json()["id"]

        set_response = client.post(
            f"/sessions/{session_id}/cookies",
            json={
                "name": "morrow_test",
                "value": "hello",
                "url": "https://example.com",
            },
        )

        assert set_response.status_code == 200

        clear_response = client.delete(
            f"/sessions/{session_id}/cookies",
        )

        assert clear_response.status_code == 200
        assert clear_response.json() == {
            "id": session_id,
            "status": "cookies_cleared",
        }

        get_response = client.get(
            f"/sessions/{session_id}/cookies",
        )

        assert get_response.status_code == 200
        assert get_response.json() == {
            "id": session_id,
            "cookies": [],
        }


def test_api_cookies_missing_session() -> None:
    """The API should return 404 for an unknown session."""
    with TestClient(app) as client:
        response = client.get(
            "/sessions/does-not-exist/cookies",
        )

        assert response.status_code == 404
        assert response.json() == {
            "detail": "Session not found",
        }


def test_api_local_storage() -> None:
    """The API should set and return localStorage values."""
    with TestClient(app) as client:
        create_response = client.post("/sessions")

        assert create_response.status_code == 201
        session_id = create_response.json()["id"]

        navigate_response = client.post(
            f"/sessions/{session_id}/navigate",
            json={"url": "https://example.com"},
        )

        assert navigate_response.status_code == 200

        set_response = client.post(
            f"/sessions/{session_id}/storage/local",
            json={
                "key": "morrow_test",
                "value": "hello",
            },
        )

        assert set_response.status_code == 200
        assert set_response.json() == {
            "id": session_id,
            "status": "local_storage_set",
            "key": "morrow_test",
        }

        get_response = client.get(
            f"/sessions/{session_id}/storage/local",
        )

        assert get_response.status_code == 200
        assert get_response.json() == {
            "id": session_id,
            "storage": {
                "morrow_test": "hello",
            },
        }


def test_api_clear_local_storage() -> None:
    """The API should clear all localStorage values."""
    with TestClient(app) as client:
        create_response = client.post("/sessions")

        assert create_response.status_code == 201
        session_id = create_response.json()["id"]

        navigate_response = client.post(
            f"/sessions/{session_id}/navigate",
            json={"url": "https://example.com"},
        )

        assert navigate_response.status_code == 200

        set_response = client.post(
            f"/sessions/{session_id}/storage/local",
            json={
                "key": "morrow_test",
                "value": "hello",
            },
        )

        assert set_response.status_code == 200

        clear_response = client.delete(
            f"/sessions/{session_id}/storage/local",
        )

        assert clear_response.status_code == 200
        assert clear_response.json() == {
            "id": session_id,
            "status": "local_storage_cleared",
        }

        get_response = client.get(
            f"/sessions/{session_id}/storage/local",
        )

        assert get_response.status_code == 200
        assert get_response.json() == {
            "id": session_id,
            "storage": {},
        }


def test_api_local_storage_missing_session() -> None:
    """The API should return 404 for an unknown session."""
    with TestClient(app) as client:
        response = client.get(
            "/sessions/does-not-exist/storage/local",
        )

        assert response.status_code == 404
        assert response.json() == {
            "detail": "Session not found",
        }


def test_api_session_storage() -> None:
    """The API should set and return sessionStorage values."""
    with TestClient(app) as client:
        create_response = client.post("/sessions")

        assert create_response.status_code == 201
        session_id = create_response.json()["id"]

        navigate_response = client.post(
            f"/sessions/{session_id}/navigate",
            json={"url": "https://example.com"},
        )

        assert navigate_response.status_code == 200

        set_response = client.post(
            f"/sessions/{session_id}/storage/session",
            json={
                "key": "morrow_test",
                "value": "hello",
            },
        )

        assert set_response.status_code == 200
        assert set_response.json() == {
            "id": session_id,
            "status": "session_storage_set",
            "key": "morrow_test",
        }

        get_response = client.get(
            f"/sessions/{session_id}/storage/session",
        )

        assert get_response.status_code == 200
        assert get_response.json() == {
            "id": session_id,
            "storage": {
                "morrow_test": "hello",
            },
        }


def test_api_clear_session_storage() -> None:
    """The API should clear all sessionStorage values."""
    with TestClient(app) as client:
        create_response = client.post("/sessions")

        assert create_response.status_code == 201
        session_id = create_response.json()["id"]

        navigate_response = client.post(
            f"/sessions/{session_id}/navigate",
            json={"url": "https://example.com"},
        )

        assert navigate_response.status_code == 200

        set_response = client.post(
            f"/sessions/{session_id}/storage/session",
            json={
                "key": "morrow_test",
                "value": "hello",
            },
        )

        assert set_response.status_code == 200

        clear_response = client.delete(
            f"/sessions/{session_id}/storage/session",
        )

        assert clear_response.status_code == 200
        assert clear_response.json() == {
            "id": session_id,
            "status": "session_storage_cleared",
        }

        get_response = client.get(
            f"/sessions/{session_id}/storage/session",
        )

        assert get_response.status_code == 200
        assert get_response.json() == {
            "id": session_id,
            "storage": {},
        }


def test_api_session_storage_missing_session() -> None:
    """The API should return 404 for an unknown session."""
    with TestClient(app) as client:
        response = client.get(
            "/sessions/does-not-exist/storage/session",
        )

        assert response.status_code == 404
        assert response.json() == {
            "detail": "Session not found",
        }

def test_api_set_local_storage_missing_session() -> None:
    """The API should return 404 when setting localStorage in an unknown session."""
    with TestClient(app) as client:
        response = client.post(
            "/sessions/does-not-exist/storage/local",
            json={
                "key": "morrow_test",
                "value": "hello",
            },
        )

        assert response.status_code == 404
        assert response.json() == {
            "detail": "Session not found",
        }


def test_api_clear_local_storage_missing_session() -> None:
    """The API should return 404 when clearing localStorage in an unknown session."""
    with TestClient(app) as client:
        response = client.delete(
            "/sessions/does-not-exist/storage/local",
        )

        assert response.status_code == 404
        assert response.json() == {
            "detail": "Session not found",
        }


def test_api_set_session_storage_missing_session() -> None:
    """The API should return 404 when setting sessionStorage in an unknown session."""
    with TestClient(app) as client:
        response = client.post(
            "/sessions/does-not-exist/storage/session",
            json={
                "key": "morrow_test",
                "value": "hello",
            },
        )

        assert response.status_code == 404
        assert response.json() == {
            "detail": "Session not found",
        }


def test_api_clear_session_storage_missing_session() -> None:
    """The API should return 404 when clearing sessionStorage in an unknown session."""
    with TestClient(app) as client:
        response = client.delete(
            "/sessions/does-not-exist/storage/session",
        )

        assert response.status_code == 404
        assert response.json() == {
            "detail": "Session not found",
        }
