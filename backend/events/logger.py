"""In-memory event recording for Morrow browser sessions."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class BrowserEvent:
    """Represents one observable browser event."""

    type: str
    timestamp: datetime
    data: dict[str, Any] = field(default_factory=dict)


class EventLogger:
    """Store browser events in memory for the lifetime of a session."""

    def __init__(self) -> None:
        self._events: list[BrowserEvent] = []

    def record(
        self,
        event_type: str,
        **data: Any,
    ) -> BrowserEvent:
        """Record an event in memory."""
        event = BrowserEvent(
            type=event_type,
            timestamp=datetime.now(UTC),
            data=data,
        )

        self._events.append(event)
        return event

    def all(self) -> list[BrowserEvent]:
        """Return all recorded events."""
        return list(self._events)

    def clear(self) -> None:
        """Discard all recorded events."""
        self._events.clear()
