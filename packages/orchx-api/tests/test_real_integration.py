import os
import pytest
from httpx import ASGITransport, AsyncClient
from orchx_api.main import app

@pytest.mark.asyncio
@pytest.mark.skipif(
    os.environ.get("ORCHX_RUN_LIVE_PROVIDER_TESTS") != "true",
    reason="ORCHX_RUN_LIVE_PROVIDER_TESTS=true not set. Skipping live external provider integration test."
)
async def test_real_provider_execution_lifecycle():
    """
    Live external provider integration test validating the entire onboarding, credentials storage,
    real API execution, and credential teardown lifecycle.
    """
    assert "ORCHX_MASTER_KEY" in os.environ, "ORCHX_MASTER_KEY must be set."
    test_api_key = os.environ.get("ORCHX_TEST_GROQ_API_KEY")
    assert test_api_key, "ORCHX_TEST_GROQ_API_KEY must be set to run live provider tests."

    # Prevent accidental leakage of the actual key in logs or test assertions
    assert len(test_api_key) > 10

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        # 1. Store credentials via the FastAPI bridge
        store_res = await client.post(
            "/api/v1/providers/credentials",
            json={
                "provider": "groq",
                "api_key": test_api_key
            }
        )
        assert store_res.status_code == 200
        
        try:
            # 2. Execute prompt using the real Groq credential
            response = await client.post(
                "/api/v1/runtime/execute",
                json={
                    "prompt": "Say exactly: 'INTEGRATION_TEST_PASS'",
                    "provider": "groq",
                    "model": "llama-3.1-8b-instant"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["provider"] == "groq"
            assert "INTEGRATION_TEST_PASS" in data["response"]
            
        finally:
            # 3. Clean up credentials from the SecretVault after test execution
            del_res = await client.delete("/api/v1/vault/providers/groq")
            assert del_res.status_code == 200
