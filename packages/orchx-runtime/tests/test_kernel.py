import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock

from orchx_core.exceptions import CapabilityViolationError, PluginLoadError
from orchx_core.interfaces.event import Event
from orchx_core.interfaces.plugin import PluginManifest, BasePlugin
from orchx_core.interfaces.provider import BaseProvider
from orchx_core.interfaces.tool import BaseTool
from orchx_runtime.bus import InMemoryEventBus
from orchx_runtime.loader import check_version_compatibility, PluginLoader
from orchx_runtime.capability import CapabilityEngine
from orchx_runtime.kernel import Kernel


# 1. Event Bus Tests
@pytest.mark.asyncio
async def test_event_bus_exact_match(event_bus: InMemoryEventBus):
    received = []

    async def handler(event: Event):
        received.append(event)

    await event_bus.subscribe("task.started", handler)
    
    event = Event(id="1", topic="task.started", payload={"data": 123})
    await event_bus.publish(event)
    
    assert len(received) == 1
    assert received[0].id == "1"
    assert received[0].topic == "task.started"


@pytest.mark.asyncio
async def test_event_bus_wildcard_routing(event_bus: InMemoryEventBus):
    received = []

    async def handler(event: Event):
        received.append(event)

    await event_bus.subscribe("*", handler)

    event_a = Event(id="1", topic="task.started")
    event_b = Event(id="2", topic="task.completed")

    await event_bus.publish(event_a)
    await event_bus.publish(event_b)

    assert len(received) == 2
    assert {e.id for e in received} == {"1", "2"}


# 2. Plugin Compatibility Check Tests
def test_plugin_semver_compatibility():
    # Compatible
    assert check_version_compatibility("0.1.0", "0.1.0") is True
    assert check_version_compatibility("0.5.2", "0.1.0") is True  # same major 0
    # Incompatible
    assert check_version_compatibility("1.0.0", "0.1.0") is False  # major mismatch
    assert check_version_compatibility("2.1.0", "1.0.0") is False  # major mismatch


# 3. Capability Validation Engine Tests
class MockPlugin(BasePlugin):
    async def install(self, ctx): pass
    async def initialize(self, ctx): pass
    async def start(self, ctx): pass
    async def pause(self, ctx): pass
    async def resume(self, ctx): pass
    async def stop(self, ctx): pass
    async def uninstall(self, ctx): pass


def test_capability_engine_authorization(kernel_context):
    engine = CapabilityEngine(kernel_context)
    
    manifest_with_cap = PluginManifest(
        id="mock-tool",
        name="Mock Tool",
        version="1.0.0",
        api_version="0.1.0",
        type="tool",
        entrypoint="test.MockTool",
        capabilities=["filesystem.read"]
    )
    
    plugin = MockPlugin(manifest_with_cap)
    
    # Authorizing approved capability should succeed
    engine.authorize_execution(plugin, "filesystem.read")
    
    # Authorizing unauthorized capability should raise error
    with pytest.raises(CapabilityViolationError):
        engine.authorize_execution(plugin, "filesystem.write")


# 4. Kernel Telemetry Tests
def test_kernel_initial_health(kernel: Kernel):
    health = kernel.health()
    assert health.status == "unhealthy"  # not started yet
    assert health.version == "0.1.0"
    assert health.uptime == 0.0
    assert len(health.loaded_components) == 0
    assert health.last_error is None
