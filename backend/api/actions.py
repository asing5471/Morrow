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
