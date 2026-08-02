import uuid
from typing import Any, Dict, List, Optional
from orchx_core.interfaces.agent_contracts import (
    CapabilityDefinition,
    CapabilityGovernanceProfile,
    AgentTemplate,
    AgentInstance,
    TeamComposition,
    CollaborationMessage,
    CollaborationProtocol,
    NegotiationProposal,
    DecisionOutcome,
    SharedWorkingContext,
    AgentLifecycleState,
    AgentSandboxPermissions
)

class CapabilityRegistry:
    """Manages permanent reusable capability definitions and resolves dependencies."""
    def __init__(self) -> None:
        self.capabilities: Dict[str, CapabilityDefinition] = {}

    def register_capability(self, cap: CapabilityDefinition) -> None:
        self.capabilities[cap.capability_id] = cap

    def resolve_dependencies(self, required_caps: List[str]) -> List[str]:
        """Resolves full dependency graph. E.g. Frontend -> Node -> Git."""
        resolved = set()
        
        def _resolve(cap_id: str):
            if cap_id in resolved:
                return
            resolved.add(cap_id)
            if cap_id in self.capabilities:
                for dep in self.capabilities[cap_id].dependencies:
                    _resolve(dep)
                    
        for cap in required_caps:
            _resolve(cap)
        return list(resolved)

class CapabilityGovernance:
    """Tracks capability trust, usage, and handles deprecation."""
    def __init__(self) -> None:
        self.profiles: Dict[str, CapabilityGovernanceProfile] = {}
        
    def log_usage(self, cap_id: str) -> None:
        if cap_id not in self.profiles:
            self.profiles[cap_id] = CapabilityGovernanceProfile(capability_id=cap_id)
        self.profiles[cap_id].execution_history_count += 1
        
    def deprecate_capability(self, cap_id: str, replacements: List[str]) -> None:
        if cap_id in self.profiles:
            self.profiles[cap_id].is_deprecated = True
            self.profiles[cap_id].replacement_recommendations = replacements

class DynamicTeamBuilder:
    """Assembles a temporary team of AgentInstances from AgentTemplates for a Goal."""
    def __init__(self, registry: CapabilityRegistry):
        self.registry = registry
        self.templates: Dict[str, AgentTemplate] = {}
        
    def register_template(self, template: AgentTemplate) -> None:
        self.templates[template.template_id] = template
        
    def build_team(self, goal_id: str, required_templates: List[str]) -> TeamComposition:
        agents = []
        for t_id in required_templates:
            if t_id in self.templates:
                t = self.templates[t_id]
                resolved_caps = self.registry.resolve_dependencies(t.capabilities)
                
                instance = AgentInstance(
                    instance_id=f"ag-{uuid.uuid4()}",
                    template_reference=t_id,
                    assigned_goal=goal_id,
                    assigned_role=t.name,
                    active_capabilities=resolved_caps,
                    sandbox_permissions=AgentSandboxPermissions(
                        allowed_capabilities=resolved_caps,
                        allowed_tools=t.supported_tools
                    )
                )
                agents.append(instance)
                
        return TeamComposition(
            team_id=f"team-{uuid.uuid4()}",
            goal_id=goal_id,
            agents=agents,
            collaboration_order=[a.instance_id for a in agents]
        )

class CollaborationEngine:
    """Routes structured collaboration messages between agent instances."""
    def __init__(self) -> None:
        self.message_log: List[CollaborationMessage] = []
        
    def send_message(self, msg: CollaborationMessage) -> bool:
        # Agents cannot use free-form text. Must use CollaborationProtocol.
        if msg.message_type not in CollaborationProtocol:
            return False
        self.message_log.append(msg)
        return True

class NegotiationEngine:
    """Evaluates multiple agent proposals to produce an objective decision outcome."""
    def evaluate_proposals(self, proposals: List[NegotiationProposal]) -> DecisionOutcome:
        if not proposals:
            raise ValueError("No proposals to negotiate")
            
        # Simplified objective evaluation: Lowest estimated cost wins
        ranked = sorted(proposals, key=lambda p: p.estimated_time_ms)
        selected = ranked[0]
        
        return DecisionOutcome(
            outcome_id=f"do-{uuid.uuid4()}",
            selected_proposal_id=selected.proposal_id,
            rejected_proposals=[p.proposal_id for p in ranked[1:]],
            reasoning=f"Selected proposal {selected.proposal_id} due to lowest estimated time.",
            confidence=0.88,
            tradeoffs={"time": "faster", "quality": "unknown"}
        )

class SharedWorkingContextManager:
    """Slices context strictly based on least privilege."""
    def create_context(self, agent: AgentInstance, full_context: Dict[str, Any]) -> SharedWorkingContext:
        # Example slice: only provide keys relevant to the agent's role
        sliced_details = {
            k: v for k, v in full_context.items()
            if "global" in k or agent.assigned_role.lower() in k
        }
        return SharedWorkingContext(
            context_id=f"ctx-{uuid.uuid4()}",
            agent_instance_id=agent.instance_id,
            sliced_goal_details=sliced_details
        )
