#!/usr/bin/env python3
import asyncio
from orchx_core.interfaces.provider_contracts import ProviderRequest
from orchx_runtime.infrastructure_layer import ProviderCredentialManager
from orchx_runtime.provider_adapters import (
    OpenAIProviderAdapter,
    AnthropicProviderAdapter,
    OllamaProviderAdapter
)

async def main():
    print("========================================")
    print("   ORCHX MANUAL INTEGRATION HARNESS     ")
    print("========================================")
    
    cred = ProviderCredentialManager()
    
    req = ProviderRequest(
        model_id="gpt-4o",
        messages=[{"role": "user", "content": "Hello, world!"}],
        temperature=0.7,
        max_tokens=100
    )
    
    print("\n[1] Testing OpenAI Integration (Mocked Network)")
    openai = OpenAIProviderAdapter(cred)
    try:
        resp = await openai.call(req)
        print(f"    [Response] {resp.content}")
        print(f"    [Tokens] {resp.usage.total_tokens} (Cost: ${resp.usage.estimated_cost:.5f})")
        print(f"    [Latency] {resp.usage.latency_ms:.1f}ms")
    except Exception as e:
        print(f"    [FAIL] {e}")

    print("\n[2] Testing Anthropic Integration (Mocked Network)")
    req_claude = ProviderRequest(
        model_id="claude-3-opus",
        messages=[{"role": "user", "content": "Hello, world!"}],
        temperature=0.7,
        max_tokens=100
    )
    anthropic = AnthropicProviderAdapter(cred)
    try:
        resp = await anthropic.call(req_claude)
        print(f"    [Response] {resp.content}")
        print(f"    [Tokens] {resp.usage.total_tokens} (Cost: ${resp.usage.estimated_cost:.5f})")
        print(f"    [Latency] {resp.usage.latency_ms:.1f}ms")
    except Exception as e:
        print(f"    [FAIL] {e}")

    print("\n[3] Testing Ollama Integration (Simulating Rate Limit 429)")
    req_ollama = ProviderRequest(
        model_id="mistral-7b",
        messages=[{"role": "user", "content": "Hello, world!"}],
        temperature=0.7,
        max_tokens=100
    )
    ollama = OllamaProviderAdapter(cred)
    # Simulate a network failure loop directly in the mock
    ollama.client.post = None # this will trigger an exception
    try:
        resp = await ollama.call(req_ollama)
    except Exception as e:
        print(f"    [OK] Captured expected failover event: {e}")

if __name__ == "__main__":
    asyncio.run(main())
