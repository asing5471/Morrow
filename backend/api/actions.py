"""Browser action API routes for Morrow."""

from fastapi import APIRouter, HTTPException, Request

from backend.browser.manager import BrowserSessionManager


router = APIRouter(prefix="/sessions", tags=["actions"])


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
