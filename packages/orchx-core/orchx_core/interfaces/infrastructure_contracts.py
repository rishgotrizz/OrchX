from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class StorageEngine(str, Enum):
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    REDIS = "redis"
    PGVECTOR = "pgvector"
    S3 = "s3"

class ConfigurationProfile(BaseModel):
    environment: str = "development"
    primary_storage_engine: StorageEngine = StorageEngine.SQLITE
    cache_engine: StorageEngine = StorageEngine.REDIS
    vector_engine: StorageEngine = StorageEngine.SQLITE
    provider_endpoints: Dict[str, str] = Field(default_factory=dict)
    feature_flags: Dict[str, bool] = Field(default_factory=dict)

class StorageMetrics(BaseModel):
    engine: str
    latency_ms: float = 0.0
    utilization_percent: float = 0.0
    cache_hit_ratio: float = 0.0
    active_connections: int = 0

class StorageEncryptionPolicy(BaseModel):
    encryption_enabled: bool = True
    key_reference_path: str = "vault/keys/storage"
    encrypted_namespaces: List[str] = Field(default_factory=lambda: ["memory", "metadata", "plugins"])

class InfrastructureHealthReport(BaseModel):
    report_id: str
    databases_healthy: bool = True
    providers_connected: bool = True
    storage_accessible: bool = True
    plugins_registered: bool = True
    vault_accessible: bool = True
    metrics: Dict[str, StorageMetrics] = Field(default_factory=dict)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Checkpoint(BaseModel):
    checkpoint_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event_stream_offset: int
    workflow_state_hash: str
    memory_state_hash: str
    agent_state_hash: str
    is_validated: bool = False

class BackupManifest(BaseModel):
    backup_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    backup_type: str = "full"
    artifacts: List[str] = Field(default_factory=list)
    encryption_enabled: bool = True
    checksum: str

class MigrationVersion(BaseModel):
    version_id: str
    applied_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    description: str
    reversible: bool = True
    schema_hash: str
