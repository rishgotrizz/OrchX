import pytest
from orchx_core.config import KernelConfig, RuntimeConfig, SecurityConfig
from orchx_runtime.bus import InMemoryEventBus
from orchx_runtime.context import KernelContext
from orchx_runtime.agent_registry import AgentRegistry
from orchx_runtime.capability_registry import CapabilityRegistry
from orchx_runtime.provider_registry import ProviderRegistry
from orchx_runtime.tool_registry import ToolRegistry
from orchx_runtime.workflow_registry import WorkflowRegistry
from orchx_runtime.kernel import Kernel


@pytest.fixture
def kernel_config() -> KernelConfig:
    return KernelConfig(
        project_name="OrchX Test OS",
        security=SecurityConfig(
            secret_key="testsecretkey",
            enable_sandbox=True
        ),
        runtime=RuntimeConfig(
            plugin_dir="test_plugins"
        )
    )


@pytest.fixture
def event_bus() -> InMemoryEventBus:
    return InMemoryEventBus()


@pytest.fixture
def registries():
    return {
        "providers": ProviderRegistry(),
        "agents": AgentRegistry(),
        "tools": ToolRegistry(),
        "workflows": WorkflowRegistry(),
        "capabilities": CapabilityRegistry()
    }


@pytest.fixture
def kernel_context(kernel_config, event_bus, registries) -> KernelContext:
    return KernelContext(
        config=kernel_config,
        event_bus=event_bus,
        provider_registry=registries["providers"],
        agent_registry=registries["agents"],
        tool_registry=registries["tools"],
        workflow_registry=registries["workflows"],
        capability_registry=registries["capabilities"]
    )


@pytest.fixture
def kernel(kernel_context) -> Kernel:
    return Kernel(kernel_context)

import httpx
import uuid
from unittest.mock import AsyncMock

from orchx_runtime.transport import TransportLayer
from typing import Dict, Any, Tuple, AsyncGenerator
import time

@pytest.fixture(autouse=True)
def mock_transport_for_golden_tests(monkeypatch):
    async def mock_execute(self, method: str, url: str, headers: Dict[str, str], json: Dict[str, Any] = None) -> Tuple[Any, Dict[str, float]]:
        telemetry = {
            "start_time": time.time(),
            "retry_count": 0,
            "http_status": 200,
            "total_duration": 50.0
        }
        
        class MockResponse:
            def __init__(self, method, url):
                self.status_code = 200
                self.method = method
                self.url = url
            def json(self):
                # If it's a discovery request
                if "v1/models" in url or "api/tags" in url or "api.moonshot.cn" in url:
                    return {"data": [{"id": "gpt-4o"}], "models": [{"name": "mistral-7b"}]}
                
                # Mock generic response payload that normalizers can parse
                return {
                    "id": f"resp-{uuid.uuid4()}",
                    "choices": [{"message": {"role": "assistant", "content": "Real parsed response payload."}, "delta": {"content": "Real parsed response payload."}}],
                    "usage": {
                        "prompt_tokens": 10,
                        "completion_tokens": 20,
                        "total_tokens": 30
                    },
                    "message": {"content": "Real parsed response payload.", "role": "assistant"},
                    "done": True,
                    "prompt_eval_count": 10,
                    "eval_count": 20,
                    "content": [{"type": "text", "text": "Real parsed response payload."}],
                    "candidates": [{"content": {"parts": [{"text": "Real parsed response payload."}]}}],
                    "usageMetadata": {"promptTokenCount": 10, "candidatesTokenCount": 20, "totalTokenCount": 30}
                }
        
        return MockResponse(method, url), telemetry

    async def mock_stream(self, method: str, url: str, headers: Dict[str, str], json: Dict[str, Any] = None) -> AsyncGenerator[Tuple[bytes, Dict[str, float]], None]:
        telemetry = {
            "start_time": time.time(),
            "first_byte_time": 10.0,
            "total_duration": 50.0,
            "http_status": 200,
            "retry_count": 0
        }
        
        # We need to yield bytes that normalizers can parse.
        # OpenAINormalizer uses 'data: {...}'
        openai_chunk = b'data: {"choices": [{"delta": {"content": "stream chunk"}}], "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}}\n'
        yield openai_chunk, telemetry
        
        # Anthropic uses type: content_block_delta
        anthropic_chunk = b'data: {"type": "content_block_delta", "delta": {"text": "stream chunk"}}\n'
        yield anthropic_chunk, telemetry
        
        # Gemini uses raw JSON array or object
        gemini_chunk = b'{"candidates": [{"content": {"parts": [{"text": "stream chunk"}]}}], "usageMetadata": {"promptTokenCount": 10, "candidatesTokenCount": 20, "totalTokenCount": 30}}\n'
        yield gemini_chunk, telemetry
        
        # Ollama
        ollama_chunk = b'{"message": {"content": "stream chunk"}, "done": true, "prompt_eval_count": 10, "eval_count": 20}\n'
        yield ollama_chunk, telemetry

    monkeypatch.setattr(TransportLayer, "execute", mock_execute)
    monkeypatch.setattr(TransportLayer, "stream", mock_stream)
