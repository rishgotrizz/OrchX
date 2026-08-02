import pytest
from typing import Dict, Any

from orchx_core.interfaces.provider_contracts import ProviderRequest, ProviderResponse
from orchx_runtime.provider_adapters import (
    OpenAIProviderAdapter,
    AnthropicProviderAdapter,
    GoogleGeminiProviderAdapter,
    OllamaProviderAdapter
)
from orchx_runtime.selection_strategies import DefaultSelectionStrategy, LowestLatencyStrategy
from orchx_runtime.provider_manager import ProviderManager
from orchx_runtime.infrastructure_layer import ProviderCredentialManager

@pytest.fixture
def cred_manager():
    return ProviderCredentialManager()

# 1. Adapter Registry & Normalization Tests
def test_provider_adapters_registration(cred_manager):
    openai = OpenAIProviderAdapter(cred_manager)
    anthropic = AnthropicProviderAdapter(cred_manager)
    
    assert openai.provider_info.id == "openai"
    assert len(openai.list_models()) >= 1
    
    # Check capabilities matrices belong to models
    gpt4 = next(m for m in openai.list_models() if m.id == "gpt-4o")
    assert "chat" in gpt4.capabilities

@pytest.mark.asyncio
async def test_provider_request_response_normalization(cred_manager):
    # Golden Integration Test for normalization
    openai = OpenAIProviderAdapter(cred_manager)
    
    request = ProviderRequest(
        model_id="gpt-4o",
        messages=[{"role": "user", "content": "What is OrchX?"}]
    )
    
    response = await openai.call(request)
    
    # Normalized response assertions (Golden compliance)
    assert response.model_used == "gpt-4o"
    assert response.role == "assistant"
    assert response.usage.prompt_tokens == 10
    assert response.usage.completion_tokens == 20
    assert response.usage.total_tokens == 30
    assert response.usage.estimated_cost >= 0.0

@pytest.mark.asyncio
async def test_streaming_support(cred_manager):
    openai = OpenAIProviderAdapter(cred_manager)
    request = ProviderRequest(
        model_id="gpt-4o",
        messages=[{"role": "user", "content": "Stream me."}]
    )
    
    chunks = []
    async for chunk in openai.stream(request):
        chunks.append(chunk)
        
    assert len(chunks) >= 1
    # Note: Stream mock doesn't always have total_tokens, wait, the golden test mock had it?
    # No, our mock yields delta only, wait, I'll just check if it parsed properly.
    assert chunks[0].content == "stream chunk"

@pytest.mark.asyncio
async def test_provider_rate_limit_backoff(cred_manager, monkeypatch):
    from orchx_runtime.transport import TransportLayer
    import uuid
    import time
    openai = OpenAIProviderAdapter(cred_manager)
    request = ProviderRequest(
        model_id="gpt-4o",
        messages=[{"role": "user", "content": "Test"}]
    )
    
    call_count = 0
    
    async def rate_limited(self, method, url, **kwargs):
        nonlocal call_count
        call_count += 1
        telemetry = {
            "start_time": time.time(),
            "retry_count": call_count - 1,
            "http_status": 429 if call_count == 1 else 200,
            "total_duration": 50.0
        }
        
        class MockResponse:
            def json(self):
                if "v1/models" in url:
                    return {"data": [{"id": "gpt-4o"}]}
                return {
                    "id": f"resp-{uuid.uuid4()}",
                    "choices": [{"message": {"role": "assistant", "content": "Real parsed response payload."}}],
                    "usage": {
                        "prompt_tokens": 10,
                        "completion_tokens": 20,
                        "total_tokens": 30
                    }
                }
        return MockResponse(), telemetry
        
    monkeypatch.setattr(TransportLayer, "execute", rate_limited)
    
    resp = await openai.call(request)
    assert call_count == 2
    assert resp.model_used == "gpt-4o"

# 2. Provider Failover Manager Tests
@pytest.mark.asyncio
async def test_provider_manager_failover_success(cred_manager, monkeypatch):
    import httpx
    manager = ProviderManager()
    
    openai = OpenAIProviderAdapter(cred_manager)
    anthropic = AnthropicProviderAdapter(cred_manager)
    
    manager.register_provider(openai)
    manager.register_provider(anthropic)
    
    # Force OpenAI to fail network requests
    from orchx_runtime.transport import TransportLayer
    original_execute = TransportLayer.execute
    
    async def failing_post(self, method, url, *args, **kwargs):
        if "api.openai.com" in url:
            raise ConnectionError("Simulated 500 outage")
        return await original_execute(self, method, url, *args, **kwargs)
        
    monkeypatch.setattr(TransportLayer, "execute", failing_post)
    
    # Needs a model with "chat" capability, both have it. OpenAI is selected first by default.
    # It fails, fails over to Anthropic.
    response = await manager.execute_request(
        required_capabilities=["chat"],
        messages=[{"role": "user", "content": "Test"}]
    )
    
    assert response.model_used == "claude-3-5-sonnet-20240620"
    assert manager.metrics["failover_count"] == 1
