"""Browser session lifecycle for Morrow."""

from dataclasses import dataclass
from uuid import uuid4


@dataclass
class BrowserSession:
    """Represents one active browser session."""

    id: str

    @classmethod
    def create(cls) -> "BrowserSession":
        """Create a new session with a unique identifier."""
        return cls(id=str(uuid4()))
