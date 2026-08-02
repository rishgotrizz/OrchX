import pytest
from orchx_core.interfaces.agent_contracts import (
    CapabilityDefinition,
    AgentTemplate,
    CollaborationMessage,
    CollaborationProtocol,
    NegotiationProposal,
    CapabilityCostModel
)
from orchx_runtime.agent_platform import (
    CapabilityRegistry,
    CapabilityGovernance,
    DynamicTeamBuilder,
    CollaborationEngine,
    NegotiationEngine,
    SharedWorkingContextManager
)

def test_capability_dependency_resolution():
    registry = CapabilityRegistry()
    registry.register_capability(CapabilityDefinition(capability_id="Frontend", name="Frontend", version="1", dependencies=["Node"]))
    registry.register_capability(CapabilityDefinition(capability_id="Node", name="Node", version="1", dependencies=["Git"]))
    registry.register_capability(CapabilityDefinition(capability_id="Git", name="Git", version="1"))
    
    resolved = registry.resolve_dependencies(["Frontend"])
    assert len(resolved) == 3
    assert set(resolved) == {"Frontend", "Node", "Git"}

def test_capability_governance():
    gov = CapabilityGovernance()
    gov.log_usage("vision_model")
    assert gov.profiles["vision_model"].execution_history_count == 1
    
    gov.deprecate_capability("vision_model", ["vision_model_v2"])
    assert gov.profiles["vision_model"].is_deprecated is True
    assert gov.profiles["vision_model"].replacement_recommendations == ["vision_model_v2"]

def test_dynamic_team_builder():
    registry = CapabilityRegistry()
    registry.register_capability(CapabilityDefinition(capability_id="React", name="React", version="18"))
    
    builder = DynamicTeamBuilder(registry)
    template = AgentTemplate(
        template_id="t-frontend",
        name="Frontend Engineer",
        description="Builds UIs",
        capabilities=["React"],
        security_profile="standard"
    )
    builder.register_template(template)
    
    team = builder.build_team("goal-404", ["t-frontend"])
    assert len(team.agents) == 1
    assert team.agents[0].assigned_role == "Frontend Engineer"
    assert "React" in team.agents[0].sandbox_permissions.allowed_capabilities

def test_collaboration_engine():
    engine = CollaborationEngine()
    msg = CollaborationMessage(
        message_id="msg-1",
        message_type=CollaborationProtocol.PROPOSAL,
        sender_instance_id="ag-1",
        recipient_instance_id="ag-2",
        payload={"plan": "build faster"}
    )
    assert engine.send_message(msg) is True
    assert len(engine.message_log) == 1

def test_negotiation_engine():
    engine = NegotiationEngine()
    p1 = NegotiationProposal(
        proposal_id="p-1", agent_instance_id="ag-1", proposed_strategy="Fast",
        estimated_cost=CapabilityCostModel(), estimated_time_ms=100.0
    )
    p2 = NegotiationProposal(
        proposal_id="p-2", agent_instance_id="ag-2", proposed_strategy="Slow",
        estimated_cost=CapabilityCostModel(), estimated_time_ms=500.0
    )
    
    outcome = engine.evaluate_proposals([p1, p2])
    assert outcome.selected_proposal_id == "p-1"
    assert "p-2" in outcome.rejected_proposals

def test_shared_working_context():
    registry = CapabilityRegistry()
    builder = DynamicTeamBuilder(registry)
    builder.register_template(AgentTemplate(template_id="t1", name="Frontend", description="", security_profile="std"))
    team = builder.build_team("goal", ["t1"])
    
    ctx_manager = SharedWorkingContextManager()
    full_context = {
        "global_config": "true",
        "frontend_routes": "app.js",
        "backend_secrets": "db_pass"
    }
    
    shared = ctx_manager.create_context(team.agents[0], full_context)
    # Frontend role should get global and frontend context, not backend
    assert "global_config" in shared.sliced_goal_details
    assert "frontend_routes" in shared.sliced_goal_details
    assert "backend_secrets" not in shared.sliced_goal_details
