"""Browser session API routes."""

from fastapi import APIRouter, HTTPException, status

from backend.browser.manager import BrowserSessionManager


router = APIRouter(prefix="/sessions", tags=["sessions"])

session_manager = BrowserSessionManager()


@router.post("", status_code=status.HTTP_201_CREATED)
def create_session() -> dict[str, str]:
    """Create a new browser session."""
    session = session_manager.create_session()

    return {
        "id": session.id,
        "status": "created",
    }


@router.get("/{session_id}")
def get_session(session_id: str) -> dict[str, str]:
    """Return information about an active browser session."""
    session = session_manager.get_session(session_id)

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
def delete_session(session_id: str) -> dict[str, str]:
    """Remove an active browser session."""
    session = session_manager.remove_session(session_id)

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    return {
        "id": session.id,
        "status": "closed",
    }
