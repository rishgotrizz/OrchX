from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TaskState(str, Enum):
    """
    Standard state lifecycle for an OrchX task.
    """
    CREATED = "created"      # Task instantiated, inputs not resolved
    READY = "ready"          # Inputs resolved, ready for queue
    QUEUED = "queued"        # Placed in the execution queue
    RUNNING = "running"      # Executing by a runner
    WAITING = "waiting"      # Paused, waiting for human approval or callback
    COMPLETED = "completed"  # Successfully finished, outputs generated
    FAILED = "failed"        # Failed, execution halted
    CANCELLED = "cancelled"  # Aborted before or during execution
    SKIPPED = "skipped"      # Bypassed by DAG conditional path
    RETRIED = "retried"      # Failed but rescheduled for retry


class TaskPriority(str, Enum):
    """Priority mapping for scheduler queue order."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskConstraint(BaseModel):
    """
    Constraint rules mapping where a task can execute.
    
    Example:
        TaskConstraint(key="os", operator="==", value="linux")
    """
    key: str = Field(..., description="Target environment factor, e.g. 'os', 'network'")
    operator: str = Field("==", description="Matching operator: '==', '!=', 'contains'")
    value: str = Field(..., description="Target value requirement")


class ResourceRequirements(BaseModel):
    """
    Resource limits requested for runner sandbox allocation.
    """
    cpu_cores: float = Field(0.5, description="Min requested CPU cores")
    memory_mb: int = Field(512, description="Min requested RAM in Megabytes")
    gpu_count: int = Field(0, description="Requested GPU count")
    temp_disk_mb: int = Field(256, description="Requested local sandbox disk allocation")


class Artifact(BaseModel):
    """
    An Artifact represents a first-class, structured piece of data consumed or 
    produced by a Task (e.g. source code files, test logs, DB schemas, bundles).
    """
    id: str = Field(..., description="Unique machine-readable identifier")
    name: str = Field(..., description="Human-readable asset name")
    kind: str = Field(..., description="Classifier kind e.g. 'source_code', 'parameter', 'test_results'")
    version: str = Field("1.0.0", description="Artifact semantic version tag")
    schema_uri: Optional[str] = Field(None, description="Schema definition file URL for structural validation")
    mime_type: str = Field("application/json", description="Standard MIME format classifier")
    producer_task_id: Optional[str] = Field(None, description="Task ID that produced this artifact")
    consumer_task_ids: List[str] = Field(default_factory=list, description="IDs of tasks consuming this artifact")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata tags and diagnostic indices")
    serialization_format: str = Field("json", description="Format identifier (e.g., 'json', 'yaml')")
    checksum: Optional[str] = Field(None, description="SHA256 file checksum for consistency checking")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Creation timestamp")
    is_intermediate: bool = Field(False, description="Flag representing short-lived workspace variables")


class RetryPolicy(BaseModel):
    """Retry settings for task failures."""
    max_retries: int = Field(3, description="Maximum reschedule iterations")
    backoff_factor: float = Field(2.0, description="Multiplier for backoff delay intervals")
    initial_delay_seconds: int = Field(5, description="Delay duration for first retry")


class Task(BaseModel):
    """
    First-class Task abstraction in OrchX.
    Represents an atomic execution unit.
    
    Example:
        Task(
            id="task-scan-01",
            name="Scan Workspace",
            type="security_scan",
            required_capabilities=["security.read"],
            inputs=["art-code-src"],
            outputs=["art-security-report"]
        )
    """
    id: str = Field(..., description="Unique task identifier, e.g. 'task-lint-01'")
    name: str = Field(..., description="Human-readable task label")
    type: str = Field(..., description="Task type registry locator key")
    description: Optional[str] = None
    status: TaskState = Field(TaskState.CREATED, description="Current execution state")
    priority: TaskPriority = Field(TaskPriority.MEDIUM, description="Queue priority level")
    
    # Inputs/Outputs bind to Artifact ID strings
    inputs: List[str] = Field(default_factory=list, description="IDs of inputs Artifacts consumed")
    outputs: List[str] = Field(default_factory=list, description="IDs of outputs Artifacts generated")
    
    dependencies: List[str] = Field(default_factory=list, description="IDs of sibling Tasks that must complete first")
    
    required_capabilities: List[str] = Field(default_factory=list, description="Capability permission strings needed")
    required_tools: List[str] = Field(default_factory=list, description="IDs of tool plugins requested")
    
    preferred_provider: Optional[str] = Field(None, description="Optional target LLM provider override")
    preferred_agent: Optional[str] = Field(None, description="Optional target Agent executor override")
    
    retry_policy: RetryPolicy = Field(default_factory=RetryPolicy)
    timeout: int = Field(3600, description="Task execution timeout in seconds")
    
    expected_input_kinds: Dict[str, str] = Field(
        default_factory=dict,
        description="Expected Artifact kinds mapped by input ID key"
    )
    
    constraints: List[TaskConstraint] = Field(default_factory=list, description="Execution environment restrictions")
    resources: ResourceRequirements = Field(default_factory=ResourceRequirements, description="Allocatable limits required")
    
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
