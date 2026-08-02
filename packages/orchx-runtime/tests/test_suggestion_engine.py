import pytest
import asyncio
from orchx_core.interfaces.suggestion_contracts import Suggestion, SuggestionPriority
from orchx_core.interfaces.event import Event
from orchx_runtime.suggestion_engine import SuggestionRegistry, SuggestionEngine
from orchx_runtime.bus import InMemoryEventBus

@pytest.fixture
def event_bus():
    return InMemoryEventBus()

@pytest.fixture
def registry():
    return SuggestionRegistry()

@pytest.fixture
def engine(event_bus, registry):
    return SuggestionEngine(event_bus, registry)

@pytest.mark.asyncio
async def test_suggestion_registry(registry):
    s = Suggestion(
        id="s1",
        priority=SuggestionPriority.HIGH,
        confidence=0.9,
        source="optimizer",
        reasoning="Test reasoning",
        estimated_impact="High impact"
    )
    await registry.register(s)
    
    suggestions = await registry.get_all()
    assert len(suggestions) == 1
    assert suggestions[0].id == "s1"
    
    fetched = await registry.get_by_id("s1")
    assert fetched is not None
    assert fetched.priority == SuggestionPriority.HIGH
    
    await registry.clear()
    assert len(await registry.get_all()) == 0

@pytest.mark.asyncio
async def test_suggestion_engine_event_handling(engine, event_bus, registry):
    await engine.start()
    
    # Publish an event to the topic
    payload = {
        "id": "s2",
        "priority": "critical",
        "confidence": 0.95,
        "source": "security",
        "reasoning": "Vulnerability found",
        "affected_components": ["auth"],
        "estimated_impact": "Critical risk"
    }
    event = Event(id="evt1", topic="system.suggestion.new", payload=payload)
    
    await event_bus.publish(event)
    
    # Yield control to allow async event processing
    await asyncio.sleep(0.1)
    
    suggestions = await registry.get_all()
    assert len(suggestions) == 1
    assert suggestions[0].id == "s2"
    assert suggestions[0].priority == SuggestionPriority.CRITICAL
    
    await engine.stop()

@pytest.mark.asyncio
async def test_suggestion_engine_ranking(engine, registry):
    s1 = Suggestion(id="s1", priority=SuggestionPriority.LOW, confidence=0.8, source="a", reasoning="b", estimated_impact="c")
    s2 = Suggestion(id="s2", priority=SuggestionPriority.CRITICAL, confidence=0.9, source="a", reasoning="b", estimated_impact="c")
    s3 = Suggestion(id="s3", priority=SuggestionPriority.HIGH, confidence=0.9, source="a", reasoning="b", estimated_impact="c")
    
    await registry.register(s1)
    await registry.register(s2)
    await registry.register(s3)
    
    ranked = await engine.get_ranked_suggestions()
    
    # Expected order: s2 (critical * 0.9 = 3.6), s3 (high * 0.9 = 2.7), s1 (low * 0.8 = 0.8)
    assert ranked[0].id == "s2"
    assert ranked[1].id == "s3"
    assert ranked[2].id == "s1"
