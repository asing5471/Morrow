"""API response and request schemas for Morrow."""

from pydantic import BaseModel


class NavigateRequest(BaseModel):
    """Request body for browser navigation."""

    url: str


class SessionResponse(BaseModel):
    """Browser session information returned by the API."""

    id: str
    status: str
    created_at: str
    current_url: str


class SessionStatusResponse(BaseModel):
    """Simple session status response."""

    id: str
    status: str


class NavigationResponse(BaseModel):
    """Response returned after navigation."""

    id: str
    status: str
    url: str


class InspectionResponse(BaseModel):
    """Response containing basic information about the current page."""

    id: str
    status: str
    url: str
    title: str
    text: str
