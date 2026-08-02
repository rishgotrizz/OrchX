import pytest
from datetime import datetime, timezone

from orchx_core.interfaces.optimization_contracts import OptimizationProfile
from orchx_core.interfaces.intelligence_contracts import Goal, RecoveryAction
from orchx_runtime.intelligence_layer import (
    GoalManager,
    ArchitectureCouncil,
    DecisionEngine,
    ReflectionEngine,
    RecoveryEngine,
)


# 1. Goal Lifecycle & Versioning Tests
def test_goal_manager_version_bumps():
    manager = GoalManager()
    
    goal = Goal(
        goal_id="g-101",
        title="Build SaaS App",
        description="Compile a web saas app",
        objectives=["Auth API", "Dashboard Panel"],
        status="pending"
    )
    
    manager.submit_goal(goal)
    assert manager.get_goal("g-101").version == "1.0.0"

    # Bump version
    new_goal = manager.bump_goal_version(
        "g-101",
        {"description": "Build premium AI SaaS App", "status": "running"}
    )
    
    assert new_goal.version == "1.1.0"
    assert new_goal.description == "Build premium AI SaaS App"
    assert new_goal.status == "running"
    assert manager.get_goal("g-101").version == "1.1.0"


# 2. Architecture Council Candidate Generation Tests
def test_architecture_council_generates_candidates():
    council = ArchitectureCouncil()
    
    goal = Goal(
        goal_id="g-1",
        title="Web Server API",
        description="Simple web api"
    )

    # 1. Generate without history
    candidates = council.generate_candidates(goal)
    assert len(candidates) == 2
    assert candidates[0].architecture_id == "arch-mono"
    assert candidates[1].architecture_id == "arch-micro"
    assert "Reused" not in candidates[0].title

    # 2. Generate with history matching
    mock_past_run = Goal(goal_id="g-past", title="Web Server API", description="Old API")
    candidates_reused = council.generate_candidates(goal, [mock_past_run])
    assert "Reused & Enhanced" in candidates_reused[0].title


# 3. DecisionEngine Weighted Rankings Tests
def test_decision_engine_profile_weighted_rankings():
    engine = DecisionEngine()
    council = ArchitectureCouncil()
    
    goal = Goal(goal_id="g-2", title="API Service", description="Scale Service")
    candidates = council.generate_candidates(goal)

    # 1. Under LOWEST_COST profile, Monolithic should win (high cost score 95.0)
    report_cost = engine.evaluate_candidates(candidates, OptimizationProfile.LOWEST_COST)
    assert report_cost.selected_candidate_id == "arch-mono"
    assert report_cost.ranking == ["arch-mono", "arch-micro"]

    # 2. Under SPEED profile, Microservices should win (high performance 90.0 & scalability 95.0)
    report_speed = engine.evaluate_candidates(candidates, OptimizationProfile.SPEED)
    assert report_speed.selected_candidate_id == "arch-micro"
    assert report_speed.ranking == ["arch-micro", "arch-mono"]


# 4. Reflection Engine Report Compilation Tests
def test_reflection_report_generation():
    engine = ReflectionEngine()
    goal = Goal(
        goal_id="g-3",
        title="Deploy App",
        description="Run scripts",
        objectives=["Compile code", "Run test suite", "Upload bundle"]
    )

    report = engine.generate_reflection(goal, ["Upload bundle task failed connection"])
    
    assert report.goal_id == "g-3"
    assert "Compile code" in report.objectives_achieved
    assert "Upload bundle task failed connection" in report.failures_encountered
    assert len(report.lessons_learned) > 0


# 5. RecoveryEngine Advisory Actions Tests
def test_recovery_engine_actions():
    engine = RecoveryEngine()

    # 1. Connection error maps to alternative provider
    plan_conn = engine.formulate_recovery("run-1", "Outage: Connection to OpenAI failed.")
    assert plan_conn.suggested_action == RecoveryAction.ALTERNATIVE_PROVIDER
    assert plan_conn.approved is False  # Must remain advisory

    # 2. Timeout error maps to alternative model
    plan_timeout = engine.formulate_recovery("run-2", "Timeout: request exceeded 30s limit.")
    assert plan_timeout.suggested_action == RecoveryAction.ALTERNATIVE_MODEL

    # 3. Memory limit error maps to alternative worker
    plan_mem = engine.formulate_recovery("run-3", "Sandbox error: OOM memory limit exceeded.")
    assert plan_mem.suggested_action == RecoveryAction.ALTERNATIVE_WORKER
