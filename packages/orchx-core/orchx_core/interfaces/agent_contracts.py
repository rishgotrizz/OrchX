from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class CollaborationProtocol(str, Enum):
    REQUEST = "request"
    RESPONSE = "response"
    PROPOSAL = "proposal"
    REVIEW = "review"
    APPROVAL = "approval"
    ESCALATION = "escalation"
    CLARIFICATION = "clarification"
    COMPLETION = "completion"

class AgentLifecycleState(str, Enum):
    CREATED = "created"
    INITIALIZED = "initialized"
    ASSIGNED = "assigned"
    COLLABORATING = "collaborating"
    WAITING = "waiting"
    REVIEWING = "reviewing"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class CapabilityCostModel(BaseModel):
    execution_cost_usd: float = 0.0
    provider_usage_tokens: int = 0
    resource_usage_cpu: float = 0.0
    latency_ms: float = 0.0
    memory_usage_mb: float = 0.0
    gpu_utilization_percent: float = 0.0

class CapabilityDefinition(BaseModel):
    capability_id: str
    name: str
    version: str
    dependencies: List[str] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list)
    trust_requirements: float = 100.0
    required_resources: Dict[str, Any] = Field(default_factory=dict)
    cost_model: CapabilityCostModel = Field(default_factory=CapabilityCostModel)

class CapabilityGovernanceProfile(BaseModel):
    capability_id: str
    trust_level: float = 100.0
    security_requirements: List[str] = Field(default_factory=list)
    execution_history_count: int = 0
    usage_statistics: Dict[str, int] = Field(default_factory=dict)
    version_compatibility: List[str] = Field(default_factory=list)
    is_deprecated: bool = False
    replacement_recommendations: List[str] = Field(default_factory=list)

class AgentSkillProfile(BaseModel):
    confidence: float = 100.0
    experience_level: str = "expert"
    historical_success_rate: float = 1.0
    preferred_workflows: List[str] = Field(default_factory=list)
    preferred_providers: List[str] = Field(default_factory=list)
    preferred_models: List[str] = Field(default_factory=list)

class AgentReputation(BaseModel):
    successful_executions: int = 0
    failed_executions: int = 0
    review_quality_score: float = 100.0
    security_incidents: int = 0
    optimization_score: float = 100.0
    collaboration_score: float = 100.0

class AgentTemplate(BaseModel):
    template_id: str
    name: str
    description: str
    capabilities: List[str] = Field(default_factory=list)
    supported_tools: List[str] = Field(default_factory=list)
    supported_workflows: List[str] = Field(default_factory=list)
    supported_provider_features: List[str] = Field(default_factory=list)
    security_profile: str
    preferred_models: List[str] = Field(default_factory=list)
    execution_constraints: Dict[str, Any] = Field(default_factory=dict)
    optimization_preferences: Dict[str, str] = Field(default_factory=dict)
    version: str = "1.0.0"

class AgentSandboxPermissions(BaseModel):
    allowed_capabilities: List[str] = Field(default_factory=list)
    allowed_tools: List[str] = Field(default_factory=list)
    allowed_providers: List[str] = Field(default_factory=list)
    allowed_memory_layers: List[str] = Field(default_factory=list)
    filesystem_scope: str = "/tmp/sandbox"
    network_scope: str = "none"

class AgentInstance(BaseModel):
    instance_id: str
    template_reference: str
    assigned_goal: str
    assigned_role: str
    current_state: AgentLifecycleState = AgentLifecycleState.CREATED
    execution_context: Dict[str, Any] = Field(default_factory=dict)
    active_capabilities: List[str] = Field(default_factory=list)
    assigned_memory: List[str] = Field(default_factory=list)
    execution_history: List[str] = Field(default_factory=list)
    skill_profile: AgentSkillProfile = Field(default_factory=AgentSkillProfile)
    reputation: AgentReputation = Field(default_factory=AgentReputation)
    sandbox_permissions: AgentSandboxPermissions = Field(default_factory=AgentSandboxPermissions)

class CollaborationMessage(BaseModel):
    message_id: str
    message_type: CollaborationProtocol
    sender_instance_id: str
    recipient_instance_id: str
    payload: Dict[str, Any]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class NegotiationProposal(BaseModel):
    proposal_id: str
    agent_instance_id: str
    proposed_strategy: str
    estimated_cost: CapabilityCostModel
    estimated_time_ms: float

class DecisionOutcome(BaseModel):
    outcome_id: str
    selected_proposal_id: str
    rejected_proposals: List[str] = Field(default_factory=list)
    reasoning: str
    confidence: float
    tradeoffs: Dict[str, str] = Field(default_factory=dict)

class ConflictResolutionReport(BaseModel):
    report_id: str
    conflict_reason: str
    resolution_outcome: str
    applied_principles: List[str] = Field(default_factory=list)

class SharedWorkingContext(BaseModel):
    context_id: str
    agent_instance_id: str
    sliced_goal_details: Dict[str, Any] = Field(default_factory=dict)
    sliced_memory_references: List[str] = Field(default_factory=list)

class TeamComposition(BaseModel):
    team_id: str
    goal_id: str
    agents: List[AgentInstance] = Field(default_factory=list)
    collaboration_order: List[str] = Field(default_factory=list)

class HumanOversightPolicy(BaseModel):
    policy_id: str
    requires_approval: bool
    reason: str
    estimated_impact: str
    risk_score: float
    confidence: float
    affected_artifacts: List[str] = Field(default_factory=list)
    rollback_strategy: Optional[str] = None

class AgentObservability(BaseModel):
    instance_id: str
    execution_timeline: List[Dict[str, Any]] = Field(default_factory=list)
    collaboration_timeline: List[Dict[str, Any]] = Field(default_factory=list)
    capability_usage: Dict[str, int] = Field(default_factory=dict)
    provider_usage: Dict[str, int] = Field(default_factory=dict)

class TeamPerformanceAnalytics(BaseModel):
    team_id: str
    collaboration_efficiency: float
    execution_time_ms: float
    review_quality: float
    security_compliance_score: float
    optimization_gains: float
    capability_utilization: float
    success_rate: float
