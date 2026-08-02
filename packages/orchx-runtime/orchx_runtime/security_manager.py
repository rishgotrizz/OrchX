import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from orchx_core.interfaces.sandbox import ExecutionContext
from orchx_core.interfaces.security_contracts import (
    SecretVault,
    SecurityPolicy,
    SecurityProfile,
    SecurityZone,
    RiskLevel,
    RiskAssessment,
    ApprovalRequest,
    ApprovalDecision,
    ApprovalRecord,
    ApprovalStatus,
    SecurityDecision,
    SecurityAuditRecord,
    TrustScore,
)


class MockSecretVault(SecretVault):
    """
    Simulates secure credentials vaults inside local memory.
    """

    def __init__(self) -> None:
        self._secrets: Dict[str, str] = {}

    async def get_secret(self, key: str) -> Optional[str]:
        return self._secrets.get(key)

    async def store_secret(self, key: str, value: str) -> None:
        self._secrets[key] = value


class SecurityManager:
    """
    Subsystem registry hosting policies, active profiles, approvals, 
    and immutable security audit ledgers.
    """

    def __init__(self, profile: SecurityProfile = SecurityProfile.DEVELOPMENT) -> None:
        self.profile = profile
        self.policies: List[SecurityPolicy] = []
        self.vault = MockSecretVault()
        self.audit_ledger: List[SecurityAuditRecord] = []
        self.approvals: Dict[str, ApprovalRecord] = {}
        self.decisions: Dict[str, SecurityDecision] = {}

    def register_policy(self, policy: SecurityPolicy) -> None:
        self.policies.append(policy)

    def log_audit(self, actor: str, action: str, target: str, policy: str, decision: str, reason: str) -> None:
        """Appends record to the immutable audit log."""
        self.audit_ledger.append(
            SecurityAuditRecord(
                actor=actor,
                action=action,
                target=target,
                policy=policy,
                decision=decision,
                reason=reason
            )
        )


class RuntimeGuard:
    """
    Execution interceptor validating permissions, resource constraints, 
    risk formulas, and security profiles before allowing task starts.
    """

    def __init__(self, manager: SecurityManager) -> None:
        self.manager = manager

    async def evaluate_execution(self, context: ExecutionContext) -> SecurityDecision:
        execution_id = context.execution_id
        task_id = context.task.id
        
        # 1. Run register policy compliance checks
        policy_explanations = []
        policy_passed = True
        for policy in self.manager.policies:
            ok, explanation = policy.validate(context)
            if not ok:
                policy_passed = False
                policy_explanations.append(explanation)
                break

        # 2. Dynamic Risk Assessment Calculator
        base_risk = 20.0
        perm_risk = 15.0 if context.task.required_capabilities else 0.0
        env_risk = 10.0 if context.worker.status != "idle" else 0.0
        net_risk = 20.0 if context.task.metadata.get("network_targets") else 0.0
        
        # Adjust risk score based on worker trust
        worker_trust = getattr(context.worker, "trust_score", 100.0)
        trust_adjust = 15.0 if worker_trust < 70.0 else 0.0
        
        overall_risk_score = min(100.0, base_risk + perm_risk + env_risk + net_risk + trust_adjust)
        
        # Map score to risk level
        if overall_risk_score <= 20.0:
            risk_level = RiskLevel.MINIMAL
        elif overall_risk_score <= 40.0:
            risk_level = RiskLevel.LOW
        elif overall_risk_score <= 60.0:
            risk_level = RiskLevel.MODERATE
        elif overall_risk_score <= 80.0:
            risk_level = RiskLevel.HIGH
        else:
            risk_level = RiskLevel.CRITICAL

        formula = (
            f"Base Risk {base_risk} + Permission Risk {perm_risk} + "
            f"Environment Risk {env_risk} + Trust Adjustment {trust_adjust} + "
            f"Network Exposure {net_risk} = Final Risk Assessment {overall_risk_score}"
        )

        assessment = RiskAssessment(
            overall_risk_score=overall_risk_score,
            risk_level=risk_level,
            confidence=0.95,
            affected_assets=[task_id],
            affected_permissions=context.task.required_capabilities,
            policies_triggered=[p.policy_name for p in self.manager.policies],
            potential_consequences=["Secret exposure", "Subprocess escape", "UI pollution"],
            mitigation_recommendations=["Create backups", "Isolate sandbox environment"],
            risk_formula_breakdown=formula
        )

        # 3. Resolve Human Approval triggers (moderate/high/critical risk >= 50.0)
        approval_state = "allowed"
        final_decision = "Allow"
        explanation = f"Execution approved. Explainable breakdown: {formula}."

        if not policy_passed:
            approval_state = "blocked_policy_violation"
            final_decision = "Deny"
            explanation = f"Execution blocked: policy compliance check failed: {'; '.join(policy_explanations)}."
        elif overall_risk_score >= 50.0:
            # Check if an approval record exists
            record = self.manager.approvals.get(execution_id)
            if not record:
                # Create pending approval request
                request = ApprovalRequest(
                    request_id=execution_id,
                    operation_name=f"Run Task {context.task.name}",
                    target_asset_id=task_id,
                    requested_by="scheduler",
                    risk_assessment=assessment,
                    status=ApprovalStatus.PENDING
                )
                record = ApprovalRecord(request=request)
                self.manager.approvals[execution_id] = record

            if record.request.status == ApprovalStatus.PENDING:
                approval_state = "pending_human_approval"
                final_decision = "Deny"
                explanation = (
                    f"Execution blocked: overall risk score {overall_risk_score} requires "
                    f"human approval. Explainable breakdown: {formula}."
                )
            elif record.request.status == ApprovalStatus.REJECTED:
                approval_state = "rejected_by_human"
                final_decision = "Deny"
                explanation = f"Execution blocked: human approval was rejected. Explanation: {formula}."
            elif record.request.status == ApprovalStatus.APPROVED:
                approval_state = "approved_by_human"
                final_decision = "Allow"
                explanation = f"Execution allowed: human approval verified. Explanation: {formula}."

        # 4. Generate SecurityDecision & Log Audits
        decision = SecurityDecision(
            decision_id=f"dec-{uuid.uuid4()}",
            execution_id=execution_id,
            evaluated_policies=[p.policy_name for p in self.manager.policies],
            evaluated_permissions=context.task.required_capabilities,
            trust_scores={"worker": worker_trust},
            approval_state=approval_state,
            final_decision=final_decision,
            explanation=explanation
        )

        self.manager.decisions[execution_id] = decision
        self.manager.log_audit(
            actor="runtime_guard",
            action="evaluate_execution",
            target=task_id,
            policy="ZeroTrustGate",
            decision=final_decision,
            reason=explanation
        )

        if final_decision == "Deny":
            raise PermissionError(explanation)

        return decision
