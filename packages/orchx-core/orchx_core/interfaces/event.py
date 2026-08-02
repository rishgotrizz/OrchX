from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Callable, Coroutine, Dict, Optional
from pydantic import BaseModel, Field


class Event(BaseModel):
    """
    Standard event packet passed through the EventBus.
    """
    id: str
    topic: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payload: Dict[str, Any] = Field(default_factory=dict)
    sender: Optional[str] = None


# Type hint for event handler coroutine callbacks
EventHandler = Callable[[Event], Coroutine[Any, Any, None]]


class EventPublisher(ABC):
    """
    Interface for components that dispatch events.
    """

    @abstractmethod
    async def publish(self, event: Event) -> None:
        """Publish an event packet to listeners."""
        pass


class EventSubscriber(ABC):
    """
    Interface for components that register listeners on topics.
    """

    @abstractmethod
    async def subscribe(self, topic: str, handler: EventHandler) -> None:
        """Register a callback coroutine to listen to a specific topic."""
        pass

    @abstractmethod
    async def unsubscribe(self, topic: str, handler: EventHandler) -> None:
        """Remove a previously registered topic callback."""
        pass


class EventBus(EventPublisher, EventSubscriber, ABC):
    """
    Combines publisher and subscriber interfaces into a single broker contract.
    """
    pass
