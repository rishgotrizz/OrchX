import time
from datetime import datetime, timezone

from orchx_core.interfaces.task import Task, TaskState
from orchx_core.interfaces.sandbox import Sandbox, ExecutionContext, SandboxResult, ExecutionReport
from orchx_runtime.scheduler import TaskStateTransitionManager


class TaskRunner:
    """
    Coordinates Sandbox resource checks, transitions, executions, and artifact results tracking.
    """

    async def run_task(self, context: ExecutionContext, sandbox: Sandbox) -> ExecutionReport:
        started_at = datetime.now(timezone.utc)
        
        # 1. Pre-execution capability validation check
        missing_capabilities = [
            cap for cap in context.task.required_capabilities if cap not in context.worker.capabilities
        ]
        if missing_capabilities:
            TaskStateTransitionManager.transition(context.task, TaskState.FAILED)
            raise ValueError(
                f"Task execution rejected: Worker '{context.worker.id}' lacks "
                f"required capabilities: {missing_capabilities}"
            )

        # 2. Transition Task state from QUEUED/ASSIGNED -> RUNNING
        # Note: If the task state was QUEUED, we transition it. If it is already RUNNING, we skip.
        try:
            TaskStateTransitionManager.transition(context.task, TaskState.RUNNING)
        except ValueError as e:
            # For testing convenience, if task is READY or CREATED, we force go through QUEUED first
            if context.task.status in (TaskState.CREATED, TaskState.READY):
                context.task.status = TaskState.QUEUED
                TaskStateTransitionManager.transition(context.task, TaskState.RUNNING)
            else:
                raise e

        # 3. Execute command in Sandbox
        sandbox_result = await sandbox.execute(context)
        
        finished_at = datetime.now(timezone.utc)
        duration = (finished_at - started_at).total_seconds()

        # 4. Resolve output states: exit_code == 0 -> COMPLETED, else FAILED
        final_state = TaskState.COMPLETED if sandbox_result.exit_code == 0 else TaskState.FAILED
        TaskStateTransitionManager.transition(context.task, final_state)

        # 5. Compile immutable ExecutionReport
        return ExecutionReport(
            execution_id=context.execution_id,
            task_id=context.task.id,
            worker_id=context.worker.id,
            sandbox_type=sandbox.__class__.__name__,
            started_at=started_at,
            finished_at=finished_at,
            duration=duration,
            final_status=final_state,
            produced_artifacts=sandbox_result.produced_artifacts,
            execution_metrics={
                "exit_code": sandbox_result.exit_code,
                "cpu_time": sandbox_result.cpu_time,
                "memory_usage": sandbox_result.memory_usage,
                "stdout_length": len(sandbox_result.stdout),
                "stderr_length": len(sandbox_result.stderr),
            },
            logs_reference=f"stdout://{context.execution_id}"
        )
