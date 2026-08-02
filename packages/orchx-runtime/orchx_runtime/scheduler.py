import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set

from orchx_core.interfaces.graph import ExecutionGraph
from orchx_core.interfaces.task import Task, TaskState
from orchx_core.interfaces.worker import Worker, WorkerLease
from orchx_core.interfaces.scheduler import (
    Scheduler,
    SchedulingDecision,
    SchedulerSnapshot,
    SchedulingPolicy,
)
from orchx_runtime.worker_registry import WorkerRegistry


class TaskStateTransitionManager:
    """
    Enforces valid state transition paths for tasks to maintain execution audit integrity.
    """

    ALLOWED_TRANSITIONS: Dict[TaskState, Set[TaskState]] = {
        TaskState.CREATED: {TaskState.READY, TaskState.SKIPPED, TaskState.CANCELLED, TaskState.FAILED},
        TaskState.READY: {TaskState.QUEUED, TaskState.SKIPPED, TaskState.CANCELLED, TaskState.FAILED},
        TaskState.QUEUED: {TaskState.RUNNING, TaskState.CANCELLED, TaskState.FAILED},  # Note: Assigned handles linking, Running maps run
        TaskState.RUNNING: {TaskState.COMPLETED, TaskState.FAILED, TaskState.WAITING, TaskState.CANCELLED},
        TaskState.WAITING: {TaskState.RUNNING, TaskState.CANCELLED},
        TaskState.COMPLETED: set(),  # Final state
        TaskState.FAILED: {TaskState.RETRIED, TaskState.CANCELLED},
        TaskState.CANCELLED: set(),  # Final state
        TaskState.SKIPPED: set(),    # Final state
        TaskState.RETRIED: {TaskState.QUEUED, TaskState.CANCELLED}
    }

    @classmethod
    def transition(cls, task: Task, next_state: TaskState) -> None:
        """
        Transition task state, raising ValueError if the path is invalid.
        Allows transition to CANCELLED from any non-final state.
        """
        current = task.status
        if current == next_state:
            return

        # CANCELLED is allowed from any state except final ones
        is_final = current in (TaskState.COMPLETED, TaskState.CANCELLED, TaskState.SKIPPED)
        if next_state == TaskState.CANCELLED and not is_final:
            task.status = next_state
            return

        valid_next = cls.ALLOWED_TRANSITIONS.get(current, set())
        if next_state not in valid_next:
            raise ValueError(
                f"Invalid task state transition: Cannot transition task '{task.id}' "
                f"from state '{current.value}' to state '{next_state.value}'."
            )
        task.status = next_state


class DependencyResolver:
    """
    Analyzes ExecutionGraph DAG node states to determine eligibility for execution.
    """

    @staticmethod
    def get_runnable_tasks(graph: ExecutionGraph) -> List[Task]:
        """
        Scan nodes in the graph. Returns a list of Tasks whose dependencies 
        are fully COMPLETED and are currently in the CREATED/READY state.
        """
        runnable = []
        for task_id, task in graph.nodes.items():
            if task.status not in (TaskState.CREATED, TaskState.READY):
                continue

            # Check dependencies
            deps_completed = True
            for dep_id in task.dependencies:
                dep_task = graph.nodes.get(dep_id)
                if not dep_task or dep_task.status != TaskState.COMPLETED:
                    deps_completed = False
                    break
            
            if deps_completed:
                runnable.append(task)
        return runnable

    @staticmethod
    def propagate_failures(graph: ExecutionGraph) -> List[str]:
        """
        Identify downstream tasks blocked by failed dependencies.
        Transitions blocked tasks to FAILED/SKIPPED and returns their IDs.
        """
        propagated = []
        
        # Simple propagation: if a direct dependency is FAILED (and not retried/running),
        # propagate failure to downstream tasks.
        changed = True
        while changed:
            changed = False
            for task_id, task in graph.nodes.items():
                if task.status in (TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELLED, TaskState.SKIPPED):
                    continue

                for dep_id in task.dependencies:
                    dep_task = graph.nodes.get(dep_id)
                    if dep_task and dep_task.status == TaskState.FAILED:
                        TaskStateTransitionManager.transition(task, TaskState.SKIPPED)
                        propagated.append(task_id)
                        changed = True
                        break
        return propagated


class DefaultScheduler(Scheduler):
    """
    Core implementation of the OrchX Scheduler.
    Ticks over registered ExecutionGraphs, routes ready queues, and leases workers.
    """

    def __init__(self, policy: SchedulingPolicy) -> None:
        self.policy = policy
        self.worker_registry = WorkerRegistry()
        self.graphs: Dict[str, ExecutionGraph] = {}
        self.leases: Dict[str, WorkerLease] = {}

    def register_worker(self, worker: Worker) -> None:
        self.worker_registry.register(worker)

    def unregister_worker(self, worker_id: str) -> Optional[Worker]:
        return self.worker_registry.unregister(worker_id)

    def submit_graph(self, graph: ExecutionGraph) -> None:
        self.graphs[graph.workflow_instance_id] = graph

    async def tick(self) -> List[SchedulingDecision]:
        """
        Evaluate dependencies, assemble the ready queue, match workers, and log decisions.
        """
        decisions: List[SchedulingDecision] = []
        
        for graph in self.graphs.values():
            # 1. Propagate dependency failures (skips downstream nodes if blocking deps failed)
            DependencyResolver.propagate_failures(graph)

            # 2. Extract runnable nodes
            runnable_tasks = DependencyResolver.get_runnable_tasks(graph)
            
            # Transition CREATED to READY
            for task in runnable_tasks:
                if task.status == TaskState.CREATED:
                    TaskStateTransitionManager.transition(task, TaskState.READY)

            # 3. Sort ready queue using active policy
            sorted_queue = self.policy.sort_queue(runnable_tasks)
            
            # 4. Attempt worker assignment
            available_workers = self.worker_registry.list_all()
            
            for task in sorted_queue:
                assigned_worker = self.policy.select_worker(task, available_workers)
                
                # Fetch baseline compatibility checks for observability logs
                constraint_checks = {}
                if assigned_worker:
                    _, constraint_checks = self.policy.verify_compatibility(task, assigned_worker)
                
                if assigned_worker:
                    # Allocate temporary worker lease reservation
                    lease_id = f"lease-{uuid.uuid4()}"
                    lease = WorkerLease(
                        lease_id=lease_id,
                        worker_id=assigned_worker.id,
                        task_id=task.id,
                        status="active"
                    )
                    self.leases[lease_id] = lease
                    
                    # Transition states READY -> QUEUED -> RUNNING (as reported)
                    # For scheduling loop, we transition task to QUEUED
                    TaskStateTransitionManager.transition(task, TaskState.QUEUED)
                    
                    # Mock worker load increment
                    assigned_worker.current_load = min(1.0, assigned_worker.current_load + 0.25)
                    
                    decisions.append(
                        SchedulingDecision(
                            task_id=task.id,
                            worker_id=assigned_worker.id,
                            scheduling_policy=self.policy.__class__.__name__,
                            decision_reason=f"Matched compatible worker '{assigned_worker.name}' satisfying constraints.",
                            constraint_checks=constraint_checks,
                            resource_summary={
                                "requested_cpu": task.resources.cpu_cores,
                                "allocated_cpu": assigned_worker.available_resources.cpu_cores
                            }
                        )
                    )
                else:
                    decisions.append(
                        SchedulingDecision(
                            task_id=task.id,
                            worker_id="none",
                            scheduling_policy=self.policy.__class__.__name__,
                            decision_reason="No compatible workers found satisfying capability or resource constraints.",
                            constraint_checks={"compat_check_failed": True},
                            resource_summary={}
                        )
                    )

        return decisions

    def get_snapshot(self) -> SchedulerSnapshot:
        """
        Assemble ready-only snapshot of tasks in all active queues.
        """
        ready_tasks = []
        blocked_tasks = []
        running_tasks = []
        completed_tasks = []

        total_queue_len = 0
        for graph in self.graphs.values():
            for task in graph.nodes.values():
                if task.status == TaskState.READY:
                    ready_tasks.append(task.id)
                    total_queue_len += 1
                elif task.status == TaskState.QUEUED:
                    total_queue_len += 1
                elif task.status == TaskState.RUNNING:
                    running_tasks.append(task.id)
                elif task.status == TaskState.COMPLETED:
                    completed_tasks.append(task.id)
                elif task.status == TaskState.CREATED:
                    # Created but not ready (blocked by dependencies)
                    blocked_tasks.append(task.id)

        return SchedulerSnapshot(
            queue_length=total_queue_len,
            ready_tasks=ready_tasks,
            blocked_tasks=blocked_tasks,
            running_tasks=running_tasks,
            completed_tasks=completed_tasks,
            worker_count=len(self.worker_registry.list_all()),
            active_policy=self.policy.__class__.__name__
        )
