import pytest
import asyncio
import os
import sqlite3
from typing import Dict

from orchx_runtime.vault import EncryptionEngine, SQLiteSecretVault, SecretAccessPolicy, SecretVaultAdapter
from orchx_runtime.infrastructure_layer import ProviderCredentialManager
from orchx_runtime.provider_metadata import ProviderMetadataRegistry

@pytest.fixture
def encryption():
    return EncryptionEngine()

@pytest.fixture
def vault(encryption):
    return SQLiteSecretVault(":memory:", encryption)

@pytest.fixture
def adapter(vault):
    return SecretVaultAdapter(vault)

@pytest.fixture
def manager(adapter):
    return ProviderCredentialManager(vault_adapter=adapter)

@pytest.fixture
def policy():
    return SecretAccessPolicy(
        service="ProviderCredentialManager",
        provider="openai",
        reason="Testing",
        request_id="test-123"
    )

def test_encryption_engine(encryption):
    plaintext = "super_secret_key"
    enc, nonce = encryption.encrypt(plaintext)
    assert enc != plaintext
    assert encryption.decrypt(enc, nonce) == plaintext

@pytest.mark.asyncio
async def test_vault_store_and_retrieve(vault, policy):
    from orchx_runtime.vault import current_vault_policy
    current_vault_policy.set(policy)
    await vault.store_secret("openai_api_key", "sk-12345")
    val = await vault.get_secret("openai_api_key")
    assert val == "sk-12345"

@pytest.mark.asyncio
async def test_vault_access_policy_rejection(vault, policy):
    from orchx_runtime.vault import current_vault_policy
    bad_policy = SecretAccessPolicy(
        service="UnknownHackerService",
        provider="openai",
        reason="I want keys",
        request_id="hacker-1"
    )
    current_vault_policy.set(bad_policy)
    with pytest.raises(PermissionError):
        await vault.store_secret("openai_api_key", "sk-123")

@pytest.mark.asyncio
async def test_vault_versioning_and_rollback(vault, policy):
    from orchx_runtime.vault import current_vault_policy
    current_vault_policy.set(policy)
    await vault.store_secret("key1", "v1")
    await vault.store_secret("key1", "v2")
    
    val = await vault.get_secret("key1")
    assert val == "v2"
    
    versions = await vault.list_versions("key1")
    assert len(versions) == 2
    assert versions[0]["active"] == 1
    assert versions[1]["active"] == 0
    
    # Rollback requires AdminCLI or WebFrontend policy
    admin_policy = SecretAccessPolicy(
        service="AdminCLI",
        provider="openai",
        reason="Rolling back",
        request_id="admin-1"
    )
    
    v1_id = versions[1]["version_id"]
    current_vault_policy.set(admin_policy)
    success = await vault.rollback_secret("key1", v1_id)
    assert success is True
    
    current_vault_policy.set(policy)
    val_after_rollback = await vault.get_secret("key1")
    assert val_after_rollback == "v1"

def test_provider_credential_manager_adapter(manager):
    errors = manager.validate_and_store("openai", {"api_key": "sk-123"})
    assert not errors
    
    val = manager.get_credential("openai")
    assert val == "sk-123"

def test_provider_metadata_registry():
    registry = ProviderMetadataRegistry()
    meta = registry.get("anthropic")
    assert meta is not None
    assert meta.display_name == "Anthropic (Claude)"
    
    errors = meta.validate_credentials({})
    assert len(errors) == 1
    assert "api_key" in errors[0]

def test_capability_discovery(manager):
    # Discovery defaults to true if api_key is present because we mock the discovery
    manager.validate_and_store("gemini", {"api_key": "AIzaSy..."})
    caps = manager.get_capabilities("gemini")
    
    assert caps.live_discovery is True
    assert "gemini-1.5-pro" in caps.models
    assert caps.vision_support is True

def test_audit_logs_record_without_leaking(vault, policy):
    from orchx_runtime.vault import current_vault_policy
    async def run():
        current_vault_policy.set(policy)
        await vault.store_secret("test_key", "PLAINTEXT_SECRET_1234")
    asyncio.run(run())
    
    # Query logs directly from SQLite
    rows = vault._conn.execute("SELECT * FROM audit_logs").fetchall()
    assert len(rows) > 0
    
    for row in rows:
        log_str = str(dict(row))
        assert "PLAINTEXT_SECRET_1234" not in log_str
        assert row["secret_key"] == "test_key"
