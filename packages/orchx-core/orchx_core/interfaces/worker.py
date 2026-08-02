from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from orchx_core.interfaces.task import ResourceRequirements


class WorkerState(str, Enum):
    """
    Standardized worker state lifecycle.
    """
    OFFLINE = "offline"
    STARTING = "starting"
    IDLE = "idle"
    BUSY = "busy"
    DRAINING = "draining"
    STOPPED = "stopped"
    FAILED = "failed"


class Worker(BaseModel):
    """
    Exposes static and dynamic capabilities of an execution worker.
    Metadata representation only—does not run code itself.
    """
    id: str = Field(..., description="Unique worker UUID")
    name: str = Field(..., description="Human-friendly worker identity label")
    capabilities: List[str] = Field(default_factory=list, description="Supported capability permissions")
    supported_task_types: List[str] = Field(default_factory=list, description="Supported registry task types")
    available_resources: ResourceRequirements = Field(default_factory=ResourceRequirements)
    current_load: float = Field(0.0, description="Load utilization indicator from 0.0 to 1.0")
    status: WorkerState = Field(WorkerState.OFFLINE, description="Current status state")
    version: str = Field("0.1.0", description="Semantic runtime version of this worker")
    trust: Optional[Any] = Field(None, description="Dynamic TrustScore verified profile")


class WorkerLease(BaseModel):
    """
    Represents a temporary, task-scoped resource reservation assigned to a Worker.
    """
    lease_id: str = Field(..., description="Unique lease UUID")
    worker_id: str = Field(..., description="Target Worker ID reservation link")
    task_id: str = Field(..., description="Target Task ID reservation link")
    acquired_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = Field("active", description="Status states: active, released, revoked")


class WorkerHeartbeat(BaseModel):
    """
    Heartbeat report packet periodically dispatched by execution workers to registry.
    """
    worker_id: str = Field(..., description="Reporting worker UUID")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: WorkerState = Field(..., description="Reporting worker runtime state")
    current_load: float = Field(0.0, description="Reporting CPU/memory load from 0.0 to 1.0")
    available_resources: ResourceRequirements = Field(..., description="Currently available resources in the sandbox")
    active_task_count: int = Field(0, description="Running tasks counter")


class IPCMessage(BaseModel):
    """
    Generic message protocol wrapper for out-of-process IPC channels.
    """
    message_id: str = Field(..., description="Unique message UUID")
    correlation_id: str = Field(..., description="Request-response linking context ID")
    sender: str = Field(..., description="Sender module locator ID")
    receiver: str = Field(..., description="Recipient module locator ID")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    protocol_version: str = Field("1.0.0", description="Schema format version tag")
    message_type: str = Field(..., description="Topic code e.g. 'task.execute', 'heartbeat'")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Custom dictionary parameters payload")
