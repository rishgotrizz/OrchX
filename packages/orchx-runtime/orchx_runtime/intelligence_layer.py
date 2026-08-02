import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from orchx_core.interfaces.optimization_contracts import OptimizationProfile
from orchx_core.interfaces.intelligence_contracts import (
    Goal,
    AgentRole,
    RecoveryAction,
    RecoveryPlan,
    ArchitectureCandidate,
    ArchitectureScore,
    ArchitectureDecisionReport,
    ReflectionReport,
)


class GoalManager:
    """
    Registry managing high-level Goal specs, accepted states, and version bumps.
    """

    def __init__(self) -> None:
        self._goals: Dict[str, Goal] = {}

    def submit_goal(self, goal: Goal) -> None:
        self._goals[goal.goal_id] = goal

    def get_goal(self, goal_id: str) -> Optional[Goal]:
        return self._goals.get(goal_id)

    def bump_goal_version(self, goal_id: str, changes: Dict[str, Any]) -> Goal:
        """Clones active goal specification and increments minor version."""
        goal = self._goals.get(goal_id)
        if not goal:
            raise ValueError(f"Goal '{goal_id}' not found.")

        # Increment semantic minor version (e.g. 1.0.0 -> 1.1.0)
        v_parts = goal.version.split(".")
        minor = int(v_parts[1]) + 1
        new_version = f"{v_parts[0]}.{minor}.0"

        # Apply updates
        new_goal = Goal(
            goal_id=goal_id,
            title=changes.get("title", goal.title),
            description=changes.get("description", goal.description),
            objectives=changes.get("objectives", goal.objectives),
            milestones=changes.get("milestones", goal.milestones),
            capabilities_required=changes.get("capabilities_required", goal.capabilities_required),
            status=changes.get("status", goal.status),
            version=new_version,
            created_at=datetime.now(timezone.utc)
        )
        self._goals[goal_id] = new_goal
        return new_goal


class ArchitectureCouncil:
    """
    Generates multiple architectural candidate designs for a goal.
    Integrates historical checks for specification reuse.
    """

    def generate_candidates(self, goal: Goal, history: List[Any] = None) -> List[ArchitectureCandidate]:
        candidates = []
        
        # Check if similar goal has run successfully in past
        reused = False
        if history:
            for past_run in history:
                if getattr(past_run, "title", "") == goal.title:
                    reused = True
                    break

        title_suffix = " (Reused & Enhanced)" if reused else ""

        # Option A: Monolithic pattern
        candidates.append(
            ArchitectureCandidate(
                architecture_id="arch-mono",
                title=f"Monolithic Service stack{title_suffix}",
                summary="Simple monolithic FastAPI service routing all API transactions.",
                technology_stack=["Python", "FastAPI", "SQLite"],
                folder_structure={"app": ["main.py", "models.py", "schemas.py"]},
                service_boundaries=["Single deployable package boundary"],
                deployment_strategy="Docker container run",
                scalability_considerations="Horizontal scaling over standard load balancing.",
                security_considerations="Single threat surface area.",
                estimated_complexity="low",
                assumptions=["Low initial query volumes"]
            )
        )

        # Option B: Microservices pattern
        candidates.append(
            ArchitectureCandidate(
                architecture_id="arch-micro",
                title="Decoupled Microservices routing",
                summary="Decoupled worker queues routed via rabbitmq message events brokers.",
                technology_stack=["Python", "FastAPI", "RabbitMQ", "Postgres"],
                folder_structure={"services": ["gateway", "workers"]},
                service_boundaries=["Gateway api boundary", "Background worker execution boundary"],
                deployment_strategy="Kubernetes pod cluster",
                scalability_considerations="Targeted auto-scaling over worker replicas.",
                security_considerations="Isolated services token validations.",
                estimated_complexity="high",
                assumptions=["High concurrent task queues volumes"]
            )
        )

        return candidates


class DecisionEngine:
    """
    Evaluates ArchitectureCandidates using profile-weighted scoring matrices.
    """

    def evaluate_candidates(
        self,
        candidates: List[ArchitectureCandidate],
        profile: OptimizationProfile
    ) -> ArchitectureDecisionReport:
        if not candidates:
            raise ValueError("No candidates submitted for evaluation.")

        weighted_scores: Dict[str, ArchitectureScore] = {}
        
        for cand in candidates:
            # 1. Compute baseline scores based on technology and complexity metadata
            if cand.architecture_id == "arch-mono":
                maintainability = 85.0
                scalability = 50.0
                performance = 70.0
                security = 75.0
                reliability = 80.0
                cost = 95.0  # Cheap
                complexity = 20.0
            else:
                maintainability = 65.0
                scalability = 95.0  # High scale
                performance = 90.0
                security = 85.0
                reliability = 90.0
                cost = 45.0  # Expensive
                complexity = 80.0

            # 2. Adjust scores based on OptimizationProfile weights
            if profile == OptimizationProfile.LOWEST_COST:
                overall = (cost * 0.6) + (maintainability * 0.2) + (scalability * 0.2)
            elif profile == OptimizationProfile.SPEED:
                overall = (performance * 0.5) + (scalability * 0.3) + (cost * 0.2)
            elif profile == OptimizationProfile.QUALITY:
                overall = (maintainability * 0.4) + (reliability * 0.4) + (security * 0.2)
            else:
                overall = (maintainability * 0.25) + (scalability * 0.25) + (cost * 0.25) + (performance * 0.25)

            weighted_scores[cand.architecture_id] = ArchitectureScore(
                maintainability=maintainability,
                scalability=scalability,
                performance=performance,
                security=security,
                reliability=reliability,
                cost=cost,
                complexity=complexity,
                overall_score=overall
            )

        # Rank candidates by overall score descending
        sorted_candidates = sorted(
            candidates, key=lambda c: weighted_scores[c.architecture_id].overall_score, reverse=True
        )
        selected = sorted_candidates[0]
        rejected = [c.architecture_id for c in sorted_candidates[1:]]

        reason = (
            f"Selected candidate '{selected.title}' scoring "
            f"{weighted_scores[selected.architecture_id].overall_score:.1f} overall under "
            f"optimization profile '{profile.value}'."
        )

        return ArchitectureDecisionReport(
            report_id=f"adr-rep-{uuid.uuid4()}",
            selected_candidate_id=selected.architecture_id,
            ranking=[c.architecture_id for c in sorted_candidates],
            confidence=0.90,
            reasoning=reason,
            weighted_scores=weighted_scores,
            tradeoffs={
                "arch-mono": "Low infrastructure cost but limited concurrent horizontal scaling.",
                "arch-micro": "High horizontal scale but increased deployment complexity and setup overhead."
            }
        )


class ReflectionEngine:
    """
    Evaluates completed executions and generates lessons learned.
    """

    def generate_reflection(self, goal: Goal, failures_list: List[str]) -> ReflectionReport:
        objectives_achieved = goal.objectives if not failures_list else goal.objectives[:-1]
        
        lessons = [
            "Maintain separate service boundaries to simplify container deployments.",
            "Verify network boundary credentials whitelist tags early."
        ]
        
        return ReflectionReport(
            report_id=f"ref-rep-{uuid.uuid4()}",
            goal_id=goal.goal_id,
            objectives_achieved=objectives_achieved,
            failures_encountered=failures_list,
            bottlenecks=["Queue wait times degraded worker utilization during microservices tests."],
            lessons_learned=lessons
        )


class RecoveryEngine:
    """
    Maps task failures to advisory recovery actions.
    """

    def formulate_recovery(self, execution_id: str, error_message: str) -> RecoveryPlan:
        # Check error types context
        if "connection" in error_message.lower():
            action = RecoveryAction.ALTERNATIVE_PROVIDER
            reason = "Connection failed. Advisory swap to alternative provider adapter."
        elif "timeout" in error_message.lower():
            action = RecoveryAction.ALTERNATIVE_MODEL
            reason = "Timeout detected. Advisory swap to a faster model instance."
        elif "memory" in error_message.lower():
            action = RecoveryAction.ALTERNATIVE_WORKER
            reason = "Resource limits hit. Advisory leasing of larger worker slot."
        else:
            action = RecoveryAction.RETRY
            reason = "General runtime execution exception. Advisory retry loop."

        return RecoveryPlan(
            plan_id=f"plan-{uuid.uuid4()}",
            execution_id=execution_id,
            suggested_action=action,
            reason=reason
        )
