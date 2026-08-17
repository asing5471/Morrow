"""Browser action API routes for Morrow."""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response
from pydantic import BaseModel

from backend.browser.manager import BrowserSessionManager


router = APIRouter(prefix="/sessions", tags=["actions"])


class ClickRequest(BaseModel):
    """Request body for clicking an element."""

    selector: str


class TypeRequest(BaseModel):
    """Request body for typing into an element."""

    selector: str
    text: str


class CookieRequest(BaseModel):
    """Request body for setting a browser cookie."""

    name: str
    value: str
    url: str


class HoverRequest(BaseModel):
    """Request body for hovering over an element."""

    selector: str


class StorageRequest(BaseModel):
    """Request body for setting a browser storage value."""

    key: str
    value: str


def get_session_manager(request: Request) -> BrowserSessionManager:
    """Return the session manager owned by the application."""
    return request.app.state.session_manager


@router.get("/{session_id}/element")
async def find_element(
    session_id: str,
    selector: str,
    request: Request,
) -> dict[str, str | bool]:
    """Check whether an element matching a CSS selector exists."""
    manager = get_session_manager(request)
    session = manager.get_session(session_id)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    return {
        "id": session.id,
        "selector": selector,
        "found": await session.find_element(selector),
    }

@router.get("/{session_id}/page")
async def get_page_dom(
    session_id: str,
    request: Request,
) -> dict[str, str]:
    """Return the current page DOM as HTML."""
    manager = get_session_manager(request)
    session = manager.get_session(session_id)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    return {
        "id": session.id,
        "html": await session.get_dom(),
    }

@router.get("/{session_id}/element/text")
async def get_element_text(
    session_id: str,
    selector: str,
    request: Request,
) -> dict[str, str]:
    """Return the text of an element matching a CSS selector."""
    manager = get_session_manager(request)
    session = manager.get_session(session_id)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    try:
        text = await session.get_element_text(selector)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return {
        "id": session.id,
        "selector": selector,
        "text": text,
    }


@router.get("/{session_id}/screenshot")
async def screenshot_session(
    session_id: str,
    request: Request,
) -> Response:
    """Return a PNG screenshot of the current browser page."""
    manager = get_session_manager(request)
    session = manager.get_session(session_id)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    return Response(
        content=await session.screenshot(),
        media_type="image/png",
    )


@router.post("/{session_id}/click")
async def click_element(
    session_id: str,
    action: ClickRequest,
    request: Request,
) -> dict[str, str]:
    """Click an element matching a CSS selector."""
    manager = get_session_manager(request)
    session = manager.get_session(session_id)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    try:
        await session.click(action.selector)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return {
        "id": session.id,
        "status": "clicked",
        "selector": action.selector,
    }


@router.post("/{session_id}/type")
async def type_into_element(
    session_id: str,
    action: TypeRequest,
    request: Request,
) -> dict[str, str]:
    """Type text into an element matching a CSS selector."""
    manager = get_session_manager(request)
    session = manager.get_session(session_id)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    try:
        await session.type_text(action.selector, action.text)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return {
        "id": session.id,
        "status": "typed",
        "selector": action.selector,
    }


@router.get("/{session_id}/cookies")
async def get_session_cookies(
    session_id: str,
    request: Request,
) -> dict[str, object]:
    """Return cookies for the browser session."""
    manager = get_session_manager(request)
    session = manager.get_session(session_id)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    return {
        "id": session.id,
        "cookies": await session.get_cookies(),
    }


@router.post("/{session_id}/cookies")
async def set_session_cookie(
    session_id: str,
    cookie: CookieRequest,
    request: Request,
) -> dict[str, str]:
    """Add a cookie to the browser session."""
    manager = get_session_manager(request)
    session = manager.get_session(session_id)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    try:
        await session.set_cookie(cookie.model_dump())
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail="Unable to set cookie",
        ) from exc

    return {
        "id": session.id,
        "status": "cookie_set",
        "name": cookie.name,
    }


@router.delete("/{session_id}/cookies")
async def clear_session_cookies(
    session_id: str,
    request: Request,
) -> dict[str, str]:
    """Clear all cookies from the browser session."""
    manager = get_session_manager(request)
    session = manager.get_session(session_id)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    await session.clear_cookies()

    return {
        "id": session.id,
        "status": "cookies_cleared",
    }


@router.post("/{session_id}/hover")
async def hover_element(
    session_id: str,
    action: HoverRequest,
    request: Request,
) -> dict[str, str]:
    """Hover over an element matching a CSS selector."""
    manager = get_session_manager(request)
    session = manager.get_session(session_id)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    try:
        await session.hover(action.selector)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return {
        "id": session.id,
        "status": "hovered",
        "selector": action.selector,
    }


@router.get("/{session_id}/storage/local")
async def get_local_storage(
    session_id: str,
    request: Request,
) -> dict[str, object]:
    """Return localStorage for the browser session."""
    manager = get_session_manager(request)
    session = manager.get_session(session_id)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    return {
        "id": session.id,
        "storage": await session.get_local_storage(),
    }

@router.get("/{session_id}/events")
async def get_session_events(
    session_id: str,
    request: Request,
) -> dict[str, object]:
    """Return in-memory browser events for a session."""
    manager = get_session_manager(request)
    session = manager.get_session(session_id)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    return {
        "id": session.id,
        "events": [
            {
                "type": event.type,
                "timestamp": event.timestamp.isoformat(),
                "data": event.data,
            }
            for event in session.event_logger.all()
        ],
    }

@router.post("/{session_id}/storage/local")
async def set_local_storage(
    session_id: str,
    storage: StorageRequest,
    request: Request,
) -> dict[str, str]:
    """Set a localStorage value for the browser session."""
    manager = get_session_manager(request)
    session = manager.get_session(session_id)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    try:
        await session.set_local_storage(storage.key, storage.value)
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail="Unable to set local storage",
        ) from exc

    return {
        "id": session.id,
        "status": "local_storage_set",
        "key": storage.key,
    }


@router.delete("/{session_id}/storage/local")
async def clear_local_storage(
    session_id: str,
    request: Request,
) -> dict[str, str]:
    """Clear localStorage for the browser session."""
    manager = get_session_manager(request)
    session = manager.get_session(session_id)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    await session.clear_local_storage()

    return {
        "id": session.id,
        "status": "local_storage_cleared",
    }


@router.get("/{session_id}/storage/session")
async def get_session_storage(
    session_id: str,
    request: Request,
) -> dict[str, object]:
    """Return sessionStorage for the browser session."""
    manager = get_session_manager(request)
    session = manager.get_session(session_id)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    return {
        "id": session.id,
        "storage": await session.get_session_storage(),
    }


@router.post("/{session_id}/storage/session")
async def set_session_storage(
    session_id: str,
    storage: StorageRequest,
    request: Request,
) -> dict[str, str]:
    """Set a sessionStorage value for the browser session."""
    manager = get_session_manager(request)
    session = manager.get_session(session_id)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    try:
        await session.set_session_storage(storage.key, storage.value)
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail="Unable to set session storage",
        ) from exc

    return {
        "id": session.id,
        "status": "session_storage_set",
        "key": storage.key,
    }


@router.delete("/{session_id}/storage/session")
async def clear_session_storage(
    session_id: str,
    request: Request,
) -> dict[str, str]:
    """Clear sessionStorage for the browser session."""
    manager = get_session_manager(request)
    session = manager.get_session(session_id)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    await session.clear_session_storage()

    return {
        "id": session.id,
        "status": "session_storage_cleared",
    }
