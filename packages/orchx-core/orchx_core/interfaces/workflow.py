from abc import ABC, abstractmethod
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from orchx_core.interfaces.task import Task, TaskPriority, RetryPolicy, TaskConstraint, ResourceRequirements


class WorkflowState(str, Enum):
    """Execution state of a workflow run instance."""
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskDefinition(BaseModel):
    """
    Template definition for a task step inside a WorkflowDefinition.
    Does not hold runtime execution state.
    """
    id: str = Field(..., description="Local ID of the step inside the workflow")
    name: str
    type: str
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    
    # Template inputs/outputs define key variables (port names) to map
    inputs: List[str] = Field(default_factory=list, description="Port names of input artifacts")
    outputs: List[str] = Field(default_factory=list, description="Port names of output artifacts")
    
    dependencies: List[str] = Field(default_factory=list, description="Local step IDs this step depends on")
    
    required_capabilities: List[str] = Field(default_factory=list)
    required_tools: List[str] = Field(default_factory=list)
    preferred_provider: Optional[str] = None
    preferred_agent: Optional[str] = None
    retry_policy: RetryPolicy = Field(default_factory=RetryPolicy)
    timeout: int = 3600
    expected_input_kinds: Dict[str, str] = Field(default_factory=dict)
    constraints: List[TaskConstraint] = Field(default_factory=list)
    resources: ResourceRequirements = Field(default_factory=ResourceRequirements)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class WorkflowDefinition(BaseModel):
    """
    Workflow Definition. A template describing WHAT execution plan should happen.
    Remains static and immutable.
    """
    id: str = Field(..., description="Unique workflow specification ID, e.g. 'web-sass-builder'")
    name: str = Field(..., description="Human-readable workflow label")
    description: Optional[str] = None
    version: str = Field("1.0.0", description="Semantic version of the definition")
    
    # JSON schemas verifying input parameters and outputs
    inputs_schema: Dict[str, Any] = Field(default_factory=dict, description="JSON Schema for inputs")
    outputs_schema: Dict[str, Any] = Field(default_factory=dict, description="JSON Schema for outputs")
    
    steps: List[TaskDefinition] = Field(..., description="List of step templates")
    required_capabilities: List[str] = Field(default_factory=list, description="Capabilities this entire workflow requests")
    validation_rules: List[str] = Field(default_factory=list, description="Additional custom integrity verification checks")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class WorkflowInstance(BaseModel):
    """
    Workflow Instance. Represents a concrete execution run of a template definition.
    Inputs are filled, and tasks are concrete executable Task instances.
    """
    id: str = Field(..., description="Unique run identifier, e.g. 'run-web-sass-104'")
    definition_id: str = Field(..., description="Target WorkflowDefinition ID template link")
    status: WorkflowState = Field(WorkflowState.CREATED)
    
    inputs: Dict[str, Any] = Field(default_factory=dict, description="Concrete values/artifacts supplied")
    outputs: Dict[str, Any] = Field(default_factory=dict, description="Concrete values/artifacts generated")
    
    tasks: List[Task] = Field(default_factory=list, description="Instantiated executable Task objects")
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    metadata: Dict[str, Any] = Field(default_factory=dict)
