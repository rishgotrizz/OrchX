from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class PluginLifecycleState(str, Enum):
    DISCOVERED = "discovered"
    DOWNLOADED = "downloaded"
    VERIFIED = "verified"
    INSTALLED = "installed"
    VALIDATED = "validated"
    ENABLED = "enabled"
    RUNNING = "running"
    UPDATING = "updating"
    DEPRECATED = "deprecated"
    DISABLED = "disabled"
    REMOVED = "removed"

class PluginIsolationLevel(str, Enum):
    TRUSTED = "trusted"
    RESTRICTED = "restricted"
    SANDBOXED = "sandboxed"
    READONLY = "readonly"

class PluginResourceQuota(BaseModel):
    cpu_cores_limit: float = 0.5
    memory_mb_limit: int = 512
    disk_mb_limit: int = 1024
    network_bandwidth_mbps: int = 10
    gpu_memory_mb_limit: int = 0
    max_execution_time_ms: int = 30000

class PluginCompatibilityMatrix(BaseModel):
    min_kernel_version: str = "1.0.0"
    max_kernel_version: str = "2.0.0"
    capability_versions: Dict[str, str] = Field(default_factory=dict)
    supported_agent_versions: List[str] = Field(default_factory=list)
    api_version: str = "v1"
    runtime_environment: str = "python3.13"
    supported_os: List[str] = Field(default_factory=lambda: ["linux", "darwin"])

class PluginManifest(BaseModel):
    plugin_id: str
    name: str
    version: str
    author: str
    description: str
    capabilities_provided: List[str] = Field(default_factory=list)
    plugin_dependencies: List[str] = Field(default_factory=list)
    supported_platforms: List[str] = Field(default_factory=list)
    supported_agent_templates: List[str] = Field(default_factory=list)
    permissions_requested: List[str] = Field(default_factory=list)
    trust_requirements: float = 100.0
    compatibility_matrix: PluginCompatibilityMatrix = Field(default_factory=PluginCompatibilityMatrix)
    resource_limits: PluginResourceQuota = Field(default_factory=PluginResourceQuota)
    security_profile: str = "standard"
    health_check_endpoint: Optional[str] = None
    update_channel: str = "stable"

class PluginTrustProfile(BaseModel):
    plugin_id: str
    signature_verified: bool = False
    integrity_checksum: str = ""
    security_history: List[str] = Field(default_factory=list)
    review_history_score: float = 100.0
    update_history: List[str] = Field(default_factory=list)
    reputation: float = 100.0
    permission_violations: int = 0

class CapabilityMetrics(BaseModel):
    capability_id: str
    execution_count: int = 0
    success_rate: float = 1.0
    average_latency_ms: float = 0.0
    failures: int = 0
    resource_usage_peak_mb: float = 0.0

class PluginHealthReport(BaseModel):
    plugin_id: str
    uptime_seconds: int = 0
    crashes: int = 0
    latency_ms: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    execution_failures: int = 0
    compatibility_failures: int = 0
    status: str = "healthy"
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PluginSelectionPolicy(BaseModel):
    prioritize_security_trust: bool = True
    prioritize_compatibility: bool = True
    user_preference_overrides: Dict[str, str] = Field(default_factory=dict)
    prioritize_optimization_profile: bool = True
    require_minimum_reputation: float = 80.0

class PluginDependencyLock(BaseModel):
    plugin_id: str
    version: str
    resolved_dependencies: Dict[str, str] = Field(default_factory=dict)
    locked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PluginAuditRecord(BaseModel):
    event_id: str
    plugin_id: str
    action: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    details: str
