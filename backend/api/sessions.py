"""Browser session API routes."""

from fastapi import APIRouter, HTTPException, Request, status

from backend.browser.manager import BrowserSessionManager


router = APIRouter(prefix="/sessions", tags=["sessions"])


def get_session_manager(request: Request) -> BrowserSessionManager:
    """Return the session manager owned by the application."""
    return request.app.state.session_manager


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_session(request: Request) -> dict[str, str]:
    """Create a new browser session."""
    manager = get_session_manager(request)
    session = await manager.create_session()

    return {
        "id": session.id,
        "status": "created",
    }


@router.get("/{session_id}")
async def get_session(
    session_id: str,
    request: Request,
) -> dict[str, str]:
    """Return information about an active browser session."""
    manager = get_session_manager(request)
    session = manager.get_session(session_id)

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    return {
        "id": session.id,
        "status": "active",
    }


@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    request: Request,
) -> dict[str, str]:
    """Close and remove an active browser session."""
    manager = get_session_manager(request)
    session = await manager.remove_session(session_id)

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    return {
        "id": session.id,
        "status": "closed",
    }
