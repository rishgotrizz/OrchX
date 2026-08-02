import asyncio
import logging
from typing import Dict, List, Optional
from orchx_core.interfaces.suggestion_contracts import Suggestion, SuggestionPriority
from orchx_core.interfaces.event import Event, EventBus

logger = logging.getLogger(__name__)

class SuggestionRegistry:
    def __init__(self) -> None:
        self._suggestions: Dict[str, Suggestion] = {}
        self._lock = asyncio.Lock()

    async def register(self, suggestion: Suggestion) -> None:
        async with self._lock:
            self._suggestions[suggestion.id] = suggestion

    async def get_all(self) -> List[Suggestion]:
        async with self._lock:
            return list(self._suggestions.values())

    async def get_by_id(self, suggestion_id: str) -> Optional[Suggestion]:
        async with self._lock:
            return self._suggestions.get(suggestion_id)

    async def clear(self) -> None:
        async with self._lock:
            self._suggestions.clear()

class SuggestionEngine:
    def __init__(self, event_bus: EventBus, registry: SuggestionRegistry) -> None:
        self._event_bus = event_bus
        self._registry = registry
        self._topic = "system.suggestion.new"

    async def start(self) -> None:
        await self._event_bus.subscribe(self._topic, self._handle_suggestion_event)
        logger.info("SuggestionEngine started and subscribed to %s", self._topic)

    async def stop(self) -> None:
        await self._event_bus.unsubscribe(self._topic, self._handle_suggestion_event)
        logger.info("SuggestionEngine stopped")

    async def _handle_suggestion_event(self, event: Event) -> None:
        payload = event.payload
        try:
            suggestion = Suggestion(**payload)
            await self._registry.register(suggestion)
            logger.debug("Registered new suggestion: %s", suggestion.id)
        except Exception as e:
            logger.error("Failed to parse or register suggestion from event %s: %s", event.id, e)

    async def get_ranked_suggestions(self) -> List[Suggestion]:
        suggestions = await self._registry.get_all()
        
        def get_score(s: Suggestion) -> float:
            priority_score = {
                SuggestionPriority.LOW: 1.0,
                SuggestionPriority.MEDIUM: 2.0,
                SuggestionPriority.HIGH: 3.0,
                SuggestionPriority.CRITICAL: 4.0
            }.get(s.priority, 1.0)
            
            return priority_score * s.confidence
            
        return sorted(suggestions, key=get_score, reverse=True)
