"""Browser session API routes."""

from fastapi import APIRouter, HTTPException, Request, status

from backend.api.schemas import (
    NavigateRequest,
    NavigationResponse,
    SessionResponse,
    SessionStatusResponse,
)
from backend.browser.manager import BrowserSessionManager

router = APIRouter(prefix="/sessions", tags=["sessions"])


def get_session_manager(request: Request) -> BrowserSessionManager:
    """Return the session manager owned by the application."""
    return request.app.state.session_manager


@router.post("", status_code=status.HTTP_201_CREATED, response_model=SessionStatusResponse)
async def create_session(request: Request) -> SessionStatusResponse:
    """Create a new browser session."""
    manager = get_session_manager(request)
    session = await manager.create_session()

    return SessionStatusResponse(
        id=session.id,
        status=session.status,
    )


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    request: Request,
) -> SessionResponse:
    """Return information about an active browser session."""
    manager = get_session_manager(request)
    session = manager.get_session(session_id)

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    return SessionResponse(
        id=session.id,
        status=session.status,
        created_at=session.created_at.isoformat(),
        current_url=session.current_url,
    )


@router.post(
    "/{session_id}/navigate",
    response_model=NavigationResponse,
)
async def navigate_session(
    session_id: str,
    navigation: NavigateRequest,
    request: Request,
) -> NavigationResponse:
    """Navigate an active browser session to a validated URL."""
    manager = get_session_manager(request)
    session = manager.get_session(session_id)

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    try:
        await session.navigate(navigation.url)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return NavigationResponse(
        id=session.id,
        status="navigated",
        url=session.current_url,
    )


@router.delete("/{session_id}", response_model=SessionStatusResponse)
async def delete_session(
    session_id: str,
    request: Request,
) -> SessionStatusResponse:
    """Close and remove an active browser session."""
    manager = get_session_manager(request)
    session = await manager.remove_session(session_id)

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    return SessionStatusResponse(
        id=session.id,
        status="closed",
    )
