"""
Tests for real SQLite-backed infrastructure persistence.
Validates that data survives across repository instantiations (simulated restart).
"""
import os
import sqlite3
import tempfile
import pytest
from orchx_runtime.infrastructure_layer import (
    StorageAdapterRegistry,
    ConnectionPoolManager,
    StorageManager,
    MemoryRepository,
    WorkflowRepository,
    AgentRepository,
    PluginRepository,
    ExecutionRepository,
    TransactionManager,
    CheckpointManager,
    BackupManager,
    MigrationManager,
    InfrastructureHealthManager,
    ProviderCredentialManager,
    MigrationVersion,
)
from orchx_core.interfaces.infrastructure_contracts import StorageEngine


@pytest.fixture
def db_path(tmp_path):
    """Real on-disk SQLite database for persistence tests."""
    return str(tmp_path / "test_orchx.db")


@pytest.fixture
def storage(db_path):
    registry = StorageAdapterRegistry()
    pool = ConnectionPoolManager()
    return StorageManager(registry, pool, db_path=db_path)


# ─────────────────────────────────────────────────────────────
# Transaction Manager
# ─────────────────────────────────────────────────────────────

def test_transaction_commit_rollback():
    tx = TransactionManager()
    tx_id = tx.begin()
    assert isinstance(tx_id, str) and tx_id
    assert tx.commit(tx_id) is True

    tx_id2 = tx.begin()
    assert tx.rollback(tx_id2) is True


# ─────────────────────────────────────────────────────────────
# Memory Repository — Real SQLite Persistence
# ─────────────────────────────────────────────────────────────

def test_memory_repository_save_and_load(storage):
    repo = MemoryRepository(storage)
    repo.save_memory("mem-001", {"content": "hello world", "layer": "working"})
    result = repo.load_memory("mem-001")
    assert result is not None
    assert result["content"] == "hello world"


def test_memory_repository_survives_restart(db_path):
    """Simulate restart: write with one StorageManager, read with a new one on the same file."""
    registry = StorageAdapterRegistry()
    pool = ConnectionPoolManager()
    sm1 = StorageManager(registry, pool, db_path=db_path)
    MemoryRepository(sm1).save_memory("mem-restart-test", {"content": "persistent memory"})
    # Close connection (simulated restart)
    sm1._conn.close()

    # New StorageManager (simulated restart) opening same file
    sm2 = StorageManager(registry, pool, db_path=db_path)
    result = MemoryRepository(sm2).load_memory("mem-restart-test")
    assert result is not None
    assert result["content"] == "persistent memory"


def test_memory_repository_list_all(storage):
    repo = MemoryRepository(storage)
    repo.save_memory("mem-a", {"content": "alpha"})
    repo.save_memory("mem-b", {"content": "beta"})
    all_items = repo.list_all()
    ids = [item["id"] for item in all_items]
    assert "mem-a" in ids
    assert "mem-b" in ids


# ─────────────────────────────────────────────────────────────
# Workflow Repository
# ─────────────────────────────────────────────────────────────

def test_workflow_repository_save_and_load(storage):
    repo = WorkflowRepository(storage)
    repo.save_workflow("wf-001", {"status": "running", "tasks": ["t1", "t2"]})
    result = repo.load_workflow("wf-001")
    assert result is not None
    assert result["status"] == "running"
    assert result["tasks"] == ["t1", "t2"]


def test_workflow_repository_survives_restart(db_path):
    registry = StorageAdapterRegistry()
    pool = ConnectionPoolManager()
    sm1 = StorageManager(registry, pool, db_path=db_path)
    WorkflowRepository(sm1).save_workflow("wf-persist", {"name": "build-api"})
    sm1._conn.close()

    sm2 = StorageManager(registry, pool, db_path=db_path)
    result = WorkflowRepository(sm2).load_workflow("wf-persist")
    assert result is not None
    assert result["name"] == "build-api"


# ─────────────────────────────────────────────────────────────
# Agent Repository
# ─────────────────────────────────────────────────────────────

def test_agent_repository(storage):
    repo = AgentRepository(storage)
    repo.save_agent("agt-001", {"role": "backend_engineer", "capabilities": ["python"]})
    result = repo.load_agent("agt-001")
    assert result is not None
    assert result["role"] == "backend_engineer"


# ─────────────────────────────────────────────────────────────
# Plugin Repository
# ─────────────────────────────────────────────────────────────

def test_plugin_repository(storage):
    repo = PluginRepository(storage)
    repo.save_plugin("git-plugin", {"version": "1.0.0", "enabled": True})
    result = repo.load_plugin("git-plugin")
    assert result is not None
    assert result["version"] == "1.0.0"
    assert result["enabled"] is True


# ─────────────────────────────────────────────────────────────
# Checkpoint Manager — Deterministic Hashes
# ─────────────────────────────────────────────────────────────

def test_checkpoint_creation_and_validation():
    manager = CheckpointManager()
    cp = manager.create_checkpoint(event_offset=1042)
    assert cp.event_stream_offset == 1042
    assert cp.is_validated is False
    assert cp.workflow_state_hash.startswith("wf_")
    assert cp.memory_state_hash.startswith("mem_")

    is_valid = manager.validate_recovery(cp)
    assert is_valid is True
    assert cp.is_validated is True


def test_checkpoint_determinism():
    m1, m2 = CheckpointManager(), CheckpointManager()
    cp1 = m1.create_checkpoint(500)
    cp2 = m2.create_checkpoint(500)
    assert cp1.workflow_state_hash == cp2.workflow_state_hash
    assert cp1.memory_state_hash == cp2.memory_state_hash


def test_tampered_checkpoint_fails_validation():
    manager = CheckpointManager()
    cp = manager.create_checkpoint(event_offset=100)
    # Tamper the hash
    cp.workflow_state_hash = "tampered_hash"
    is_valid = manager.validate_recovery(cp)
    assert is_valid is False
    assert cp.is_validated is False


# ─────────────────────────────────────────────────────────────
# Backup Manager — Real Checksum
# ─────────────────────────────────────────────────────────────

def test_backup_manager_real_checksum():
    mgr = BackupManager()
    backup = mgr.create_backup(["db/orchx.db", "checkpoints/cp-001.json"])
    assert backup.backup_id.startswith("bkup-")
    assert backup.checksum is not None
    assert len(backup.checksum) == 64  # SHA-256 hex digest
    assert backup.encryption_enabled is True


# ─────────────────────────────────────────────────────────────
# Migration Manager
# ─────────────────────────────────────────────────────────────

def test_migration_manager_tracks_versions():
    mgr = MigrationManager()
    v1 = MigrationVersion(version_id="v1.0.0", description="Initial schema", schema_hash="abc")
    v2 = MigrationVersion(version_id="v1.1.0", description="Add index", schema_hash="def")
    assert mgr.apply_migration(v1) is True
    assert mgr.apply_migration(v2) is True
    assert len(mgr.applied_versions) == 2
    applied = mgr.list_applied()
    assert "v1.0.0" in applied
    assert "v1.1.0" in applied


def test_migration_manager_idempotent():
    """Applying the same migration twice must not error or double-count."""
    mgr = MigrationManager()
    v = MigrationVersion(version_id="v1.0.0", description="Initial schema", schema_hash="abc")
    mgr.apply_migration(v)
    mgr.apply_migration(v)  # Second call — should be idempotent
    assert len(mgr.list_applied()) == 1


def test_migration_manager_real_ddl():
    """MigrationManager must execute real DDL statements."""
    mgr = MigrationManager()
    v = MigrationVersion(
        version_id="v1.0.0",
        description="CREATE TABLE IF NOT EXISTS test_table (id TEXT PRIMARY KEY, val TEXT)",
        schema_hash="xyz",
    )
    mgr.apply_migration(v)
    # Verify table was actually created
    row = mgr._conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='test_table'").fetchone()
    assert row is not None


# ─────────────────────────────────────────────────────────────
# Infrastructure Health
# ─────────────────────────────────────────────────────────────

def test_infrastructure_health_readiness():
    mgr = InfrastructureHealthManager()
    report = mgr.check_readiness()
    assert report.databases_healthy is True
    assert report.vault_accessible is True
    assert report.storage_accessible is True


# ─────────────────────────────────────────────────────────────
# Provider Credential Manager — Vault Isolation
# ─────────────────────────────────────────────────────────────

def test_credential_manager_vault_isolation():
    """Credential manager must never read from environment variables."""
    import os
    os.environ.pop("OPENAI_API_KEY", None)
    cred = ProviderCredentialManager()
    key = cred.get_credential("openai")
    # Must return a credential from vault stub, not raise
    assert isinstance(key, str) and len(key) > 0


def test_credential_rotation():
    cred = ProviderCredentialManager()
    result = cred.rotate_credential("openai", "new-rotated-key")
    assert result is True
    # Key after rotation still fetchable (vault stub returns stub key)
    key = cred.get_credential("openai")
    assert key is not None
