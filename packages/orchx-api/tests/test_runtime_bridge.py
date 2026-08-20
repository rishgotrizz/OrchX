import os
import sqlite3
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from fastapi import FastAPI

from orchx_core.config import KernelConfig, SecurityConfig, RuntimeConfig
from orchx_runtime.bus import InMemoryEventBus
from orchx_runtime.context import KernelContext
from orchx_runtime.agent_registry import AgentRegistry
from orchx_runtime.capability_registry import CapabilityRegistry
from orchx_runtime.provider_registry import ProviderRegistry
from orchx_runtime.tool_registry import ToolRegistry
from orchx_runtime.workflow_registry import WorkflowRegistry
from orchx_runtime.kernel import Kernel
from orchx_runtime.provider_manager import ProviderManager
from orchx_runtime.vault import SQLiteSecretVault, SecretVaultAdapter
from orchx_runtime.infrastructure_layer import ProviderCredentialManager

# Import the FastAPI app
from orchx_api.main import app


@pytest_asyncio.fixture(scope="function")
async def setup_test_kernel_state():
    """
    Setup custom test state with isolated provider manager and registry.
    """
    # Create configuration
    config = KernelConfig(
        project_name="OrchX Test OS",
        security=SecurityConfig(
            secret_key="testsecretkey",
            enable_sandbox=True
        ),
        runtime=RuntimeConfig(
            plugin_dir="test_plugins"
        )
    )
    event_bus = InMemoryEventBus()
    provider_registry = ProviderRegistry()
    
    # Initialize vault
    vault = SQLiteSecretVault(":memory:")
    vault_adapter = SecretVaultAdapter(vault)
    cred_manager = ProviderCredentialManager(vault_adapter)
    
    context = KernelContext(
        config=config,
        event_bus=event_bus,
        provider_registry=provider_registry,
        agent_registry=AgentRegistry(),
        tool_registry=ToolRegistry(),
        workflow_registry=WorkflowRegistry(),
        capability_registry=CapabilityRegistry()
    )
    
    # Instantiate custom provider manager
    provider_manager = ProviderManager()
    context.register_service("provider_manager", provider_manager)
    
    kernel = Kernel(context)
    app.state.kernel = kernel
    app.state.kernel_context = context
    
    from orchx_api.api.v1 import vault_routes
    vault_routes.global_cred_manager = cred_manager
    
    yield app
    
    # Clean up
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_runtime_execute_validation_error(setup_test_kernel_state):
    """
    Validate that malformed execution payloads fail with HTTP 422.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.post(
            "/api/v1/runtime/execute",
            json={"wrong_field": "data"}  # missing prompt
        )
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_runtime_execute_success(setup_test_kernel_state):
    """
    Validate a successful execute request.
    """
    from orchx_runtime.provider_adapters import OpenAIProviderAdapter
    from unittest.mock import AsyncMock
    
    kernel = app.state.kernel
    cred_manager = kernel.context.provider_registry.get
    
    # Register mock OpenAI provider
    openai = OpenAIProviderAdapter(cred_manager)
    # Monkeypatch has_credentials and call
    openai.has_credentials = True
    
    from orchx_core.interfaces.provider_contracts import ProviderResponse, UsageMetrics
    mock_resp = ProviderResponse(
        id="resp-123",
        content="Hello world",
        model_used="openai/gpt-4o",
        finish_reason="stop",
        usage=UsageMetrics(prompt_tokens=10, completion_tokens=20, total_tokens=30, latency_ms=150.0)
    )
    openai.call = AsyncMock(return_value=mock_resp)
    
    kernel.context.provider_registry.register(openai)
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.post(
            "/api/v1/runtime/execute",
            json={
                "prompt": "Test query",
                "provider": "openai",
                "model": "gpt-4o"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["response"] == "Hello world"
        assert data["provider"] == "openai"
        assert data["model"] == "openai/gpt-4o"
        assert "latency_ms" in data
        assert "request_id" in data
        
        # Ensure API key or credentials are not returned in the payload
        assert "api_key" not in data
        assert "secret" not in data


@pytest.mark.asyncio
async def test_credential_storage(setup_test_kernel_state):
    """
    Validate credentials endpoint stores the credential successfully and doesn't leak it.
    """
    from orchx_api.api.v1 import vault_routes
    cred_manager = vault_routes.global_cred_manager
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.post(
            "/api/v1/providers/credentials",
            json={
                "provider": "groq",
                "api_key": "gsk_test_api_key_12345"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["provider"] == "groq"
        assert data["status"] == "stored"
        
        # Ensure key is not returned
        assert "gsk_test_api_key_12345" not in str(data)
        
        # Verify it was written to the SecretVault
        from orchx_runtime.vault import SecretAccessPolicy
        policy = SecretAccessPolicy(
            service="ProviderCredentialManager",
            provider="groq",
            reason="Verification",
            request_id="test"
        )
        stored_secret = cred_manager.vault_adapter.get_secret_sync("groq_api_key", policy)
        assert stored_secret == "gsk_test_api_key_12345"


def test_persistent_vault_missing_master_key_fail_fast():
    """
    Ensure SQLiteSecretVault raises ValueError if db exists but ORCHX_MASTER_KEY is missing.
    """
    db_file = "test_temp_persistent.db"
    # Ensure file exists
    with open(db_file, "w") as f:
        f.write("")
        
    # Ensure env variable is cleared
    old_key = os.environ.pop("ORCHX_MASTER_KEY", None)
    
    try:
        with pytest.raises(ValueError) as excinfo:
            SQLiteSecretVault(db_file)
        assert "ORCHX_MASTER_KEY" in str(excinfo.value)
    finally:
        # Cleanup
        if os.path.exists(db_file):
            os.remove(db_file)
        if old_key is not None:
            os.environ["ORCHX_MASTER_KEY"] = old_key


@pytest.mark.asyncio
async def test_auth_error_classification_and_fallback(setup_test_kernel_state):
    """
    Ensure auth errors (ValueError/PermissionError/401/403 status code) cause failover
    to next provider without triggering circuit breaker state changes.
    """
    from orchx_runtime.provider_adapters import OpenAIProviderAdapter, AnthropicProviderAdapter
    from unittest.mock import AsyncMock
    import httpx
    
    kernel = app.state.kernel
    cred_manager = kernel.context.provider_registry.get
    
    openai = OpenAIProviderAdapter(cred_manager)
    anthropic = AnthropicProviderAdapter(cred_manager)
    
    # Configure both as having credentials and active
    openai.has_credentials = True
    anthropic.has_credentials = True
    
    # Make OpenAI raise an authentication error (PermissionError)
    openai.call = AsyncMock(side_effect=PermissionError("Decryption failed or invalid actor"))
    
    # Make Anthropic succeed
    from orchx_core.interfaces.provider_contracts import ProviderResponse, UsageMetrics
    mock_resp = ProviderResponse(
        id="resp-anthropic",
        content="Success from Anthropic",
        model_used="anthropic/claude-3-5",
        finish_reason="stop",
        usage=UsageMetrics(prompt_tokens=10, completion_tokens=20, total_tokens=30, latency_ms=100.0)
    )
    anthropic.call = AsyncMock(return_value=mock_resp)
    
    # Register in registry
    kernel.context.provider_registry.register(openai)
    kernel.context.provider_registry.register(anthropic)
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.post(
            "/api/v1/runtime/execute",
            json={
                "prompt": "Hello"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["response"] == "Success from Anthropic"
        assert data["provider"] == "anthropic"
        
        # Verify circuit breaker of OpenAI is NOT opened
        assert openai.failure_flag is False


@pytest.mark.asyncio
async def test_transient_failure_circuit_breaker_opening(setup_test_kernel_state):
    """
    Ensure transient failures (ConnectionError/TimeoutError/5xx) open circuit breakers.
    """
    from orchx_runtime.provider_adapters import OpenAIProviderAdapter
    from unittest.mock import AsyncMock
    
    kernel = app.state.kernel
    cred_manager = kernel.context.provider_registry.get
    
    openai = OpenAIProviderAdapter(cred_manager)
    openai.has_credentials = True
    openai.call = AsyncMock(side_effect=ConnectionError("Server unreachable"))
    
    kernel.context.provider_registry.register(openai)
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.post(
            "/api/v1/runtime/execute",
            json={
                "prompt": "Hello",
                "provider": "openai"
            }
        )
        # Should fail since there's only one provider and it fails with ConnectionError
        assert response.status_code == 500
        
        # Verify circuit breaker is opened
        assert openai.failure_flag is True


@pytest.mark.asyncio
async def test_consolidated_all_provider_failure(setup_test_kernel_state):
    """
    Ensure a consolidated failure is returned when all eligible providers fail.
    """
    from orchx_runtime.provider_adapters import OpenAIProviderAdapter
    from unittest.mock import AsyncMock
    
    kernel = app.state.kernel
    cred_manager = kernel.context.provider_registry.get
    
    openai = OpenAIProviderAdapter(cred_manager)
    openai.has_credentials = True
    openai.call = AsyncMock(side_effect=ValueError("Invalid config"))
    
    kernel.context.provider_registry.register(openai)
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.post(
            "/api/v1/runtime/execute",
            json={
                "prompt": "Hello"
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert "[PROVIDER_AUTH_FAILED]" in data["detail"]


@pytest.mark.asyncio
async def test_zero_provider_execution_error_behavior(setup_test_kernel_state):
    """
    Ensure zero configured providers returns a 400 Bad Request error with a friendly message.
    """
    kernel = app.state.kernel
    # Clear all registered providers
    kernel.context.provider_registry._providers = {}
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.post(
            "/api/v1/runtime/execute",
            json={
                "prompt": "Hello"
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert "No AI providers are configured yet" in data["detail"]


@pytest.mark.asyncio
async def test_credential_deletion_and_replacement(setup_test_kernel_state):
    """
    Ensure we can replace and delete credentials securely.
    """
    from orchx_api.api.v1 import vault_routes
    cred_manager = vault_routes.global_cred_manager
    
    # 1. Store initial credential
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        res = await client.post(
            "/api/v1/providers/credentials",
            json={
                "provider": "openai",
                "api_key": "sk-initial-12345"
            }
        )
        assert res.status_code == 200
        assert cred_manager.get_credential("openai") == "sk-initial-12345"
        
        # 2. Replace with new credential
        res = await client.post(
            "/api/v1/providers/credentials",
            json={
                "provider": "openai",
                "api_key": "sk-new-98765"
            }
        )
        assert res.status_code == 200
        assert cred_manager.get_credential("openai") == "sk-new-98765"
        
        # 3. Delete credential via endpoint
        res = await client.delete(
            "/api/v1/vault/providers/openai"
        )
        assert res.status_code == 200
        with pytest.raises(ValueError):
            cred_manager.get_credential("openai")


def test_jwt_config_production_modes_and_secrets():
    import importlib
    from unittest.mock import patch
    from orchx_api.core import auth

    # Test production variations with missing/invalid secrets
    envs_to_test = ["production", "PRODUCTION", " production ", "Production"]
    invalid_secrets = ["", "   ", None]
    
    for env in envs_to_test:
        for secret in invalid_secrets:
            patch_dict = {"ORCHX_ENV": env}
            if secret is not None:
                patch_dict["ORCHX_JWT_SECRET"] = secret
            else:
                if "ORCHX_JWT_SECRET" in os.environ:
                    # Delete the key by setting it to empty string or patching around it
                    patch_dict["ORCHX_JWT_SECRET"] = ""
            
            with patch.dict(os.environ, patch_dict):
                with pytest.raises(ValueError) as excinfo:
                    importlib.reload(auth)
                assert "ORCHX_JWT_SECRET" in str(excinfo.value)

    # Test explicit secret works in production
    with patch.dict(os.environ, {"ORCHX_ENV": "production", "ORCHX_JWT_SECRET": "my-explicit-secret"}):
        importlib.reload(auth)
        assert auth.SECRET_KEY == "my-explicit-secret"

    # Test development and unset environment fallback
    dev_envs = ["development", "DEVELOPMENT", " development ", "", "   "]
    for dev_env in dev_envs:
        with patch.dict(os.environ, {"ORCHX_ENV": dev_env, "ORCHX_JWT_SECRET": ""}):
            importlib.reload(auth)
            assert len(auth.SECRET_KEY) == 64  # hex key of 32 bytes

    # Test unset environment variable entirely defaults to development
    with patch.dict(os.environ, {"ORCHX_JWT_SECRET": ""}):
        if "ORCHX_ENV" in os.environ:
            orig = os.environ.pop("ORCHX_ENV")
            try:
                importlib.reload(auth)
                assert len(auth.SECRET_KEY) == 64
            finally:
                os.environ["ORCHX_ENV"] = orig
        else:
            importlib.reload(auth)
            assert len(auth.SECRET_KEY) == 64


@pytest.mark.asyncio
async def test_runtime_execute_structured_error_and_sanitization(setup_test_kernel_state):
    from orchx_runtime.provider_adapters import OpenAIProviderAdapter
    from unittest.mock import AsyncMock
    kernel = app.state.kernel
    # Clear other registered providers
    kernel.context.provider_registry._providers = {}
    
    # Register a provider that raises ValueError (auth failure) containing sensitive key values
    openai = OpenAIProviderAdapter(kernel.context.provider_registry.get)
    openai.has_credentials = True
    openai.call = AsyncMock(side_effect=ValueError("Failed auth using key: gsk_leak_api_key_value_here"))
    kernel.context.provider_registry.register(openai)
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.post(
            "/api/v1/runtime/execute",
            json={"prompt": "Hello"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "[PROVIDER_AUTH_FAILED]" in data["detail"]
        assert "gsk_leak_api_key_value_here" not in data["detail"]


@pytest.mark.asyncio
async def test_runtime_execute_arbitrary_secrets_sanitization(setup_test_kernel_state):
    from orchx_runtime.provider_adapters import OpenAIProviderAdapter
    from unittest.mock import AsyncMock
    kernel = app.state.kernel
    
    sensitive_phrases = [
        "authentication failed: MY_SUPER_SECRET_VALUE",
        "token=abcdef123456789",
        "Authorization: Bearer totally-different-secret",
        "database password: hidden-password",
        "internal credential xyz987654321",
        "secret key is: super-key-here"
    ]
    
    for phrase in sensitive_phrases:
        openai = OpenAIProviderAdapter(kernel.context.provider_registry.get)
        openai.has_credentials = True
        openai.call = AsyncMock(side_effect=ValueError(phrase))
        
        # Register in-place
        kernel.context.provider_registry._providers = {openai.provider_info.id: openai}
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
            response = await client.post(
                "/api/v1/runtime/execute",
                json={"prompt": "Hello"}
            )
            assert response.status_code == 400
            data = response.json()
            # The client receives only safe structured codes and predefined messages
            assert "detail" in data
            assert phrase not in data["detail"]


@pytest.mark.asyncio
async def test_store_credentials_error_sanitization(setup_test_kernel_state):
    import json
    unique_secret = "MY_UNEXPECTED_VAL_XYZ_12345"
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.post(
            "/api/v1/providers/credentials",
            json={
                "provider": "unknown_prov",
                "api_key": unique_secret
            }
        )
        assert response.status_code in (400, 500)
        data = response.json()
        resp_text = json.dumps(data)
        assert unique_secret not in resp_text
