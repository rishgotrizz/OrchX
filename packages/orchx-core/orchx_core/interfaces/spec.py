from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class Requirement(BaseModel):
    """
    Represent an atomic, structured requirement.
    Includes an immutable ID for downstream Task/Artifact traceability.
    """
    id: str = Field(..., description="Stable requirement ID, e.g. 'REQ-FUN-001'")
    description: str = Field(..., description="Human statement of need")
    priority: str = Field("medium", description="Priority weight: low, medium, high")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CategorizedRequirements(BaseModel):
    """Organizes requirements into structured OS-level domains."""
    functional: List[Requirement] = Field(default_factory=list)
    non_functional: List[Requirement] = Field(default_factory=list)
    security: List[Requirement] = Field(default_factory=list)
    performance: List[Requirement] = Field(default_factory=list)
    ux: List[Requirement] = Field(default_factory=list)
    deployment: List[Requirement] = Field(default_factory=list)
    testing: List[Requirement] = Field(default_factory=list)
    documentation: List[Requirement] = Field(default_factory=list)


class ClarificationQuestion(BaseModel):
    """
    Structured questions generated when requirements are ambiguous or have low confidence.
    """
    id: str = Field(..., description="Unique clarification identifier")
    field: str = Field(..., description="Target property name in specification")
    question: str = Field(..., description="Clarifying prompt to present to the user")
    options: List[str] = Field(default_factory=list, description="Recommended choice tags")
    reason: str = Field(..., description="Why this information is required to select/compile workflows")


class ProductSpecification(BaseModel):
    """
    The immutable single source of truth specification representing analyzed user intent.
    Every update creates a new version referencing its parent.
    """
    project_name: str
    project_type: str = Field(..., description="Classifier e.g., 'web_saas', 'api_service'")
    project_description: str
    
    # Versioning Audit
    version: str = Field("1.0.0", description="Semantic version of this specification")
    parent_version: Optional[str] = Field(None, description="Previous version reference for change logs")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    author_source: str = Field("user", description="Author identifier, e.g., 'user', 'agent'")
    change_summary: Optional[str] = Field(None, description="Detailed summary explaining modifications")

    # Grouped Requirements
    requirements: CategorizedRequirements = Field(default_factory=CategorizedRequirements)
    
    goals: List[str] = Field(default_factory=list)
    target_platforms: List[str] = Field(default_factory=list)
    technology_preferences: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    acceptance_criteria: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    
    # Confidence metrics: maps field name -> confidence score (0.0 to 1.0)
    confidence_scores: Dict[str, float] = Field(
        default_factory=dict, 
        description="Confidence scores assigned by extractor to avoid assumptions"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PlanningReport(BaseModel):
    """
    Metadata representation summarizing a single Planner analysis output.
    Used for analytical review and audit logging.
    """
    specification_version: str = Field(..., description="Target version of the parsed ProductSpecification")
    planning_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    workflow_selected: str = Field(..., description="WorkflowDefinition template matched")
    planner_confidence: float = Field(..., description="Calculated average confidence score (0.0 to 1.0)")
    clarification_count: int = Field(0, description="Number of questions generated during parsing")
    warning_count: int = Field(0, description="Validation warnings reported")
    unsupported_features: List[str] = Field(default_factory=list)
    estimated_complexity: str = Field("medium", description="Estimated code complexity level, e.g. low/medium/high")
    estimated_task_count: int = Field(0, description="Predicted compiled task count")
    estimated_agent_count: int = Field(0, description="Predicted required agent workers")
    planning_duration: float = Field(0.0, description="Planner parsing duration in seconds")
    planner_version: str = Field("0.1.0", description="Semantic version of the planning module")
