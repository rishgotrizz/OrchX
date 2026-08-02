import pytest
from datetime import datetime, timezone

from orchx_core.interfaces.task import Task, ResourceRequirements
from orchx_core.interfaces.worker import Worker, WorkerLease
from orchx_core.interfaces.sandbox import ExecutionContext
from orchx_core.interfaces.security_contracts import SecurityProfile, ApprovalStatus, ApprovalDecision, TrustScore
from orchx_runtime.security_policies import FilesystemIsolationPolicy, NetworkBoundaryPolicy
from orchx_runtime.security_manager import SecurityManager, RuntimeGuard


# 1. Secret Vault Fetching Tests
@pytest.mark.asyncio
async def test_secret_vault_stores_and_retrieves():
    manager = SecurityManager()
    vault = manager.vault
    
    await vault.store_secret("api_key", "secret-123-abc")
    val = await vault.get_secret("api_key")
    assert val == "secret-123-abc"


# 2. Filesystem & Network Policy Isolation Blocks Tests
def test_filesystem_isolation_policy():
    policy = FilesystemIsolationPolicy()
    
    # 1. Valid path inside project
    ctx_ok = ExecutionContext(
        execution_id="exec-1",
        task=Task(id="t1", name="Clone", type="git"),
        worker=Worker(id="w1", name="W1"),
        lease=WorkerLease(lease_id="l1", worker_id="w1", task_id="t1"),
        working_directory="/Users/macbook/orchx/workspace"
    )
    ok, msg = policy.validate(ctx_ok)
    assert ok is True

    # 2. Invalid path linked to root system folder
    ctx_bad = ExecutionContext(
        execution_id="exec-2",
        task=Task(id="t2", name="Wipe", type="git"),
        worker=Worker(id="w1", name="W1"),
        lease=WorkerLease(lease_id="l2", worker_id="w1", task_id="t2"),
        working_directory="/etc/nginx"
    )
    ok_bad, msg_bad = policy.validate(ctx_bad)
    assert ok_bad is False
    assert "Violation" in msg_bad


# 3. RuntimeGuard Execution Validation & Explainable Risk Assessments
@pytest.mark.asyncio
async def test_runtime_guard_risk_formulas():
    manager = SecurityManager()
    guard = RuntimeGuard(manager)

    # Base worker and task under low risk (Minimal)
    task = Task(id="t1", name="Build code", type="compile")
    worker = Worker(id="w1", name="W1", status="idle")
    lease = WorkerLease(lease_id="l1", worker_id="w1", task_id="t1")
    
    ctx = ExecutionContext(
        execution_id="exec-01",
        task=task,
        worker=worker,
        lease=lease,
        working_directory="/Users/macbook/orchx"
    )

    decision = await guard.evaluate_execution(ctx)
    assert decision.final_decision == "Allow"
    assert "Base Risk" in decision.explanation
    
    # Verify audit ledger updated
    assert len(manager.audit_ledger) == 1
    assert manager.audit_ledger[0].decision == "Allow"


# 4. Human Approval Flow Triggers & Blocks
@pytest.mark.asyncio
async def test_runtime_guard_human_approval_blocks_until_approved():
    manager = SecurityManager()
    guard = RuntimeGuard(manager)

    # Highly sensitive task requiring capabilities (increases risk >= 50)
    task = Task(
        id="t-db",
        name="Delete Database",
        type="shell",
        required_capabilities=["database.delete"],
        metadata={"network_targets": ["api.openai.com"]}  # trigger net risk
    )
    worker = Worker(id="w-admin", name="W-Admin", status="idle")
    # Set worker trust score low to increase risk score further
    worker.trust = TrustScore(score=50.0, confidence=1.0, reason="Low trust simulation")
    lease = WorkerLease(lease_id="l-db", worker_id="w-admin", task_id="t-db")

    ctx = ExecutionContext(
        execution_id="exec-db-delete",
        task=task,
        worker=worker,
        lease=lease,
        working_directory="/Users/macbook/orchx"
    )

    # 1. Evaluating execution should trigger approval requirement and block
    with pytest.raises(PermissionError) as excinfo:
        await guard.evaluate_execution(ctx)

    assert "requires human approval" in str(excinfo.value)
    
    # Check that a pending approval request exists in registry
    record = manager.approvals.get("exec-db-delete")
    assert record is not None
    assert record.request.status == ApprovalStatus.PENDING
    assert record.request.risk_assessment.overall_risk_score >= 50.0

    # 2. Simulate User Approval
    record.request.status = ApprovalStatus.APPROVED
    record.decision = ApprovalDecision(
        decision_id="dec-app-1",
        request_id="exec-db-delete",
        approver="user",
        decision="approve",
        timestamp=datetime.now(timezone.utc),
        comment="Explicit approval given for production database maintenance"
    )

    # 3. Evaluating execution again should now allow it cleanly!
    decision_ok = await guard.evaluate_execution(ctx)
    assert decision_ok.final_decision == "Allow"
    assert decision_ok.approval_state == "approved_by_human"
