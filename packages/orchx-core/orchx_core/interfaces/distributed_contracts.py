from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class NodeCapability(str, Enum):
    CPU = "cpu"
    GPU = "gpu"
    CUDA = "cuda"
    APPLE_SILICON = "apple_silicon"
    LOCAL_LLM = "local_llm"
    BROWSER = "browser"
    PLAYWRIGHT = "playwright"
    DOCKER = "docker"
    BLENDER = "blender"
    THREEJS = "threejs"
    VISION = "vision"
    IMAGE_GENERATION = "image_generation"
    DEPLOYMENT = "deployment"

class NodeRole(str, Enum):
    COORDINATOR = "coordinator"
    EXECUTION = "execution"
    GPU_COMPUTE = "gpu_compute"
    CREATIVE = "creative"
    MEMORY = "memory"
    REVIEW = "review"
    SECURITY = "security"
    BUILDER = "builder"
    DEPLOYMENT = "deployment"

class FaultDomain(str, Enum):
    SINGLE_NODE = "single_node"
    AVAILABILITY_ZONE = "availability_zone"
    PROVIDER = "provider"
    STORAGE = "storage"
    NETWORK = "network"
    SCHEDULER = "scheduler"

class ResourceProfile(BaseModel):
    cpu_cores: int = 0
    memory_mb: int = 0
    gpu_memory_mb: int = 0
    disk_mb: int = 0
    network_bandwidth_mbps: int = 0
    provider_quotas: Dict[str, int] = Field(default_factory=dict)
    utilization_percentage: float = 0.0

class NodeReputation(BaseModel):
    trust_score: float = 100.0
    successful_executions: int = 0
    failed_executions: int = 0
    recovery_events: int = 0
    average_latency_ms: float = 0.0
    uptime_seconds: int = 0
    security_incidents: int = 0
    synchronization_reliability: float = 100.0

class NodeHealthProfile(BaseModel):
    status: str = "healthy"
    last_heartbeat: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    latency_ms: float = 0.0
    reputation: NodeReputation = Field(default_factory=NodeReputation)

class NodeProfile(BaseModel):
    node_id: str
    hardware_profile: str
    operating_system: str
    architecture: str
    capabilities: List[str] = Field(default_factory=list)
    roles: List[str] = Field(default_factory=list)
    fault_domain: str = FaultDomain.SINGLE_NODE.value
    resource_profile: ResourceProfile = Field(default_factory=ResourceProfile)
    health_profile: NodeHealthProfile = Field(default_factory=NodeHealthProfile)

class WorkerAdvertisement(BaseModel):
    worker_id: str
    node_id: str
    capabilities: List[str] = Field(default_factory=list)
    available_tools: List[str] = Field(default_factory=list)
    provider_access: List[str] = Field(default_factory=list)
    resource_limits: ResourceProfile
    trust_score: float = 100.0
    current_utilization: float = 0.0

class DistributedEvent(BaseModel):
    event_id: str
    event_type: str
    payload: Dict[str, Any]
    source_node: str
    target_node: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    requires_ack: bool = False
    is_replay: bool = False

class ClusterReport(BaseModel):
    active_nodes: int
    total_cpu: int
    total_memory: int
    fault_domain_distribution: Dict[str, int]
    healthy_nodes: int
    degraded_nodes: int

class SynchronizationReport(BaseModel):
    sync_id: str
    node_id: str
    conflicts_detected: int
    conflicts_resolved: int
    sync_latency_ms: float
    status: str

class DistributedExecutionDNA(BaseModel):
    node_id: str
    execution_timeline: List[Dict[str, Any]] = Field(default_factory=list)
    artifacts: List[str] = Field(default_factory=list)
    telemetry: Dict[str, Any] = Field(default_factory=dict)
    provider_usage: Dict[str, int] = Field(default_factory=dict)
    worker_identity: str
    synchronization_history: List[str] = Field(default_factory=list)

class SimulationReport(BaseModel):
    simulation_id: str
    scenario: str
    simulated_node_failures: int
    simulated_sync_delays_ms: float
    recovery_success_rate: float
    advisory_recommendations: List[str] = Field(default_factory=list)

class TaskMigrationPlan(BaseModel):
    task_id: str
    source_node: str
    target_node: str
    reason: str
    estimated_migration_cost_ms: float
