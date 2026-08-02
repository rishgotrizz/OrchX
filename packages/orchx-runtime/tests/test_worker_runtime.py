import pytest
from datetime import datetime, timezone
from typing import Dict, Any

from orchx_core.interfaces.task import Task, TaskState, ResourceRequirements
from orchx_core.interfaces.worker import Worker, WorkerState, WorkerLease, WorkerHeartbeat, IPCMessage
from orchx_core.interfaces.sandbox import ExecutionContext, SandboxResult
from orchx_runtime.worker_lifecycle import WorkerLifecycleManager
from orchx_runtime.sandbox_local import LocalProcessSandbox
from orchx_runtime.task_runner import TaskRunner


# 1. Worker State & Lifecycle Transitions Tests
def test_worker_lifecycle_transitions():
    worker = Worker(
        id="w-test",
        name="Test Worker",
        capabilities=[],
        supported_task_types=[],
        status=WorkerState.OFFLINE
    )

    # OFFLINE -> STARTING is valid
    WorkerLifecycleManager.transition(worker, WorkerState.STARTING)
    assert worker.status == WorkerState.STARTING

    # STARTING -> IDLE is valid
    WorkerLifecycleManager.transition(worker, WorkerState.IDLE)
    assert worker.status == WorkerState.IDLE
    assert worker.current_load == 0.0

    # IDLE -> BUSY is valid
    WorkerLifecycleManager.transition(worker, WorkerState.BUSY)
    assert worker.status == WorkerState.BUSY
    assert worker.current_load == 0.8

    # BUSY -> OFFLINE is invalid
    with pytest.raises(ValueError):
        WorkerLifecycleManager.transition(worker, WorkerState.OFFLINE)


# 2. Heartbeat Validation Tests
def test_worker_heartbeat_contract():
    heartbeat = WorkerHeartbeat(
        worker_id="w-test",
        status=WorkerState.IDLE,
        current_load=0.2,
        available_resources=ResourceRequirements(cpu_cores=2.0, memory_mb=2048),
        active_task_count=1
    )

    assert heartbeat.worker_id == "w-test"
    assert heartbeat.status == WorkerState.IDLE
    assert heartbeat.active_task_count == 1
    assert isinstance(heartbeat.timestamp, datetime)


# 3. IPC Message Contracts Tests
def test_ipc_message_contract():
    msg = IPCMessage(
        message_id="msg-101",
        correlation_id="corr-202",
        sender="kernel",
        receiver="worker-1",
        message_type="task.execute",
        payload={"command": "echo 'OrchX'"}
    )

    assert msg.message_id == "msg-101"
    assert msg.payload["command"] == "echo 'OrchX'"
    assert msg.protocol_version == "1.0.0"


# 4. LocalProcessSandbox Executions Tests
@pytest.mark.asyncio
async def test_local_process_sandbox_execution():
    task = Task(
        id="t-shell",
        name="Shell run",
        type="shell_run",
        metadata={"command": "echo 'OrchX Local Process Sandbox test output'"}
    )
    worker = Worker(id="w1", name="W1", status=WorkerState.IDLE)
    lease = WorkerLease(lease_id="l1", worker_id="w1", task_id="t-shell")
    
    context = ExecutionContext(
        execution_id="exec-909",
        task=task,
        worker=worker,
        lease=lease,
        working_directory="."
    )

    sandbox = LocalProcessSandbox()
    result = await sandbox.execute(context)

    assert result.execution_id == "exec-909"
    assert result.exit_code == 0
    assert "OrchX Local Process Sandbox test output" in result.stdout
    assert result.execution_duration > 0.0


# 5. TaskRunner Capability Checks and Reporting Tests
@pytest.mark.asyncio
async def test_task_runner_success_flow():
    task = Task(
        id="t-script",
        name="Run Script",
        type="python",
        required_capabilities=["filesystem.write"],
        outputs=["results_file"],
        metadata={"command": "echo 'Script complete'"}
    )
    worker = Worker(
        id="w-python",
        name="Python Worker",
        capabilities=["filesystem.write"], # Worker satisfies capabilities
        supported_task_types=["python"],
        status=WorkerState.IDLE
    )
    lease = WorkerLease(lease_id="l2", worker_id="w-python", task_id="t-script")
    
    context = ExecutionContext(
        execution_id="exec-111",
        task=task,
        worker=worker,
        lease=lease,
        working_directory="."
    )

    runner = TaskRunner()
    sandbox = LocalProcessSandbox()
    
    report = await runner.run_task(context, sandbox)

    assert report.execution_id == "exec-111"
    assert report.final_status == TaskState.COMPLETED
    assert len(report.produced_artifacts) == 1
    assert report.produced_artifacts[0] == "art-exec-111-results_file"
    assert report.execution_metrics["exit_code"] == 0
    assert task.status == TaskState.COMPLETED


@pytest.mark.asyncio
async def test_task_runner_capability_mismatch_rejection():
    task = Task(
        id="t-secure",
        name="Secure Action",
        type="python",
        required_capabilities=["network.outbound"]
    )
    worker = Worker(
        id="w-isolated",
        name="Isolated Worker",
        capabilities=[], # Missing network capability
        status=WorkerState.IDLE
    )
    lease = WorkerLease(lease_id="l3", worker_id="w-isolated", task_id="t-secure")
    
    context = ExecutionContext(
        execution_id="exec-222",
        task=task,
        worker=worker,
        lease=lease,
        working_directory="."
    )

    runner = TaskRunner()
    sandbox = LocalProcessSandbox()

    # Pre-execution checks should reject task due to missing network capability
    with pytest.raises(ValueError) as excinfo:
        await runner.run_task(context, sandbox)

    assert "lacks required capabilities" in str(excinfo.value)
    assert task.status == TaskState.FAILED
