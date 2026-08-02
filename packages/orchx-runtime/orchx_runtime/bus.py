import asyncio
from collections import defaultdict
from typing import Dict, List
from orchx_core.interfaces.event import Event, EventBus, EventHandler


class InMemoryEventBus(EventBus):
    """
    Asynchronous, in-memory implementation of the EventBus interface.
    """

    def __init__(self) -> None:
        self._subscribers: Dict[str, List[EventHandler]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def publish(self, event: Event) -> None:
        """Publish event asynchronously to all subscribed callbacks."""
        topic = event.topic
        handlers = []

        # Thread-safe access to handlers list
        async with self._lock:
            if topic in self._subscribers:
                handlers.extend(self._subscribers[topic])
            # Wildcard subscription support
            if "*" in self._subscribers:
                handlers.extend(self._subscribers["*"])

        if not handlers:
            return

        # Fire callbacks concurrently
        tasks = [asyncio.create_task(handler(event)) for handler in handlers]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def subscribe(self, topic: str, handler: EventHandler) -> None:
        """Add a callback listener for a topic."""
        async with self._lock:
            if handler not in self._subscribers[topic]:
                self._subscribers[topic].append(handler)

    async def unsubscribe(self, topic: str, handler: EventHandler) -> None:
        """Remove a callback listener."""
        async with self._lock:
            if topic in self._subscribers and handler in self._subscribers[topic]:
                self._subscribers[topic].remove(handler)
