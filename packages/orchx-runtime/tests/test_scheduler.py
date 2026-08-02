import pytest
from typing import Dict, Any

from orchx_core.interfaces.graph import ExecutionGraph
from orchx_core.interfaces.task import Task, TaskState, TaskPriority, TaskConstraint, ResourceRequirements
from orchx_core.interfaces.worker import Worker, WorkerState
from orchx_runtime.scheduler import (
    DependencyResolver,
    TaskStateTransitionManager,
    DefaultScheduler
)
from orchx_runtime.policies import FIFOPolicy, PriorityPolicy


# 1. Dependency Resolution & Cycle Propagation
def test_dependency_resolver_runnable():
    t1 = Task(id="t1", name="Clone", type="git", status=TaskState.COMPLETED)
    t2 = Task(id="t2", name="Lint", type="lint", status=TaskState.CREATED, dependencies=["t1"])
    t3 = Task(id="t3", name="Test", type="test", status=TaskState.CREATED, dependencies=["t2"])

    graph = ExecutionGraph(
        workflow_instance_id="run-dep-01",
        nodes={"t1": t1, "t2": t2, "t3": t3},
        edges={"t2": ["t1"], "t3": ["t2"]}
    )

    # t1 is completed, so t2 is now ready/runnable
    runnable = DependencyResolver.get_runnable_tasks(graph)
    assert len(runnable) == 1
    assert runnable[0].id == "t2"


def test_dependency_resolver_failures():
    t1 = Task(id="t1", name="Clone", type="git", status=TaskState.FAILED)
    t2 = Task(id="t2", name="Lint", type="lint", status=TaskState.CREATED, dependencies=["t1"])

    graph = ExecutionGraph(
        workflow_instance_id="run-fail-01",
        nodes={"t1": t1, "t2": t2},
        edges={"t2": ["t1"]}
    )

    # Failed dependency propagates down, skipping t2
    skipped = DependencyResolver.propagate_failures(graph)
    assert len(skipped) == 1
    assert skipped[0] == "t2"
    assert t2.status == TaskState.SKIPPED


# 2. State Transition Management
def test_task_state_transitions():
    task = Task(id="t1", name="Task 1", type="test", status=TaskState.CREATED)

    # CREATED -> READY is valid
    TaskStateTransitionManager.transition(task, TaskState.READY)
    assert task.status == TaskState.READY

    # READY -> QUEUED is valid
    TaskStateTransitionManager.transition(task, TaskState.QUEUED)
    assert task.status == TaskState.QUEUED

    # QUEUED -> RUNNING is valid
    TaskStateTransitionManager.transition(task, TaskState.RUNNING)
    assert task.status == TaskState.RUNNING

    # RUNNING -> COMPLETED is valid
    TaskStateTransitionManager.transition(task, TaskState.COMPLETED)
    assert task.status == TaskState.COMPLETED

    # COMPLETED -> RUNNING is invalid
    with pytest.raises(ValueError):
        TaskStateTransitionManager.transition(task, TaskState.RUNNING)


# 3. Pluggable Policies Tests
def test_scheduler_fifo_policy():
    t1 = Task(id="t1", name="Task 1", type="test", priority=TaskPriority.LOW)
    t2 = Task(id="t2", name="Task 2", type="test", priority=TaskPriority.HIGH)
    
    policy = FIFOPolicy()
    queue = [t1, t2]
    sorted_q = policy.sort_queue(queue)
    assert sorted_q == [t1, t2]  # FIFO preserves sequence


def test_scheduler_priority_policy():
    t1 = Task(id="t1", name="Task 1", type="test", priority=TaskPriority.LOW)
    t2 = Task(id="t2", name="Task 2", type="test", priority=TaskPriority.CRITICAL)
    
    policy = PriorityPolicy()
    queue = [t1, t2]
    sorted_q = policy.sort_queue(queue)
    assert sorted_q == [t2, t1]  # Priority sorts critical first


# 4. Resource & Constraint Matching
def test_resource_and_capability_matching():
    task = Task(
        id="t1",
        name="Task 1",
        type="eslint",
        required_capabilities=["filesystem.read"],
        resources=ResourceRequirements(cpu_cores=2.0, memory_mb=1024)
    )

    w_incompatible = Worker(
        id="w1",
        name="Worker 1",
        capabilities=[], # Missing capabilities
        supported_task_types=["eslint"],
        available_resources=ResourceRequirements(cpu_cores=4.0, memory_mb=2048),
        status=WorkerState.IDLE
    )

    w_insufficient_resources = Worker(
        id="w2",
        name="Worker 2",
        capabilities=["filesystem.read"],
        supported_task_types=["eslint"],
        available_resources=ResourceRequirements(cpu_cores=1.0, memory_mb=512), # Not enough cpu
        status=WorkerState.IDLE
    )

    w_compatible = Worker(
        id="w3",
        name="Worker 3",
        capabilities=["filesystem.read"],
        supported_task_types=["eslint"],
        available_resources=ResourceRequirements(cpu_cores=2.0, memory_mb=1024),
        status=WorkerState.IDLE
    )

    policy = FIFOPolicy()
    assert policy.select_worker(task, [w_incompatible]) is None
    assert policy.select_worker(task, [w_insufficient_resources]) is None
    assert policy.select_worker(task, [w_compatible]) == w_compatible


# 5. Core Scheduler Loop Verification
@pytest.mark.asyncio
async def test_scheduler_tick_and_leasing():
    scheduler = DefaultScheduler(FIFOPolicy())

    worker = Worker(
        id="w1",
        name="Main Worker",
        capabilities=["filesystem.read"],
        supported_task_types=["git"],
        available_resources=ResourceRequirements(cpu_cores=4.0, memory_mb=4096),
        status=WorkerState.IDLE
    )
    scheduler.register_worker(worker)

    t1 = Task(
        id="t1",
        name="Clone",
        type="git",
        required_capabilities=["filesystem.read"],
        status=TaskState.CREATED
    )
    graph = ExecutionGraph(
        workflow_instance_id="run-lease-01",
        nodes={"t1": t1},
        edges={"t1": []}
    )
    scheduler.submit_graph(graph)

    # Tick the scheduler
    decisions = await scheduler.tick()

    assert len(decisions) == 1
    assert decisions[0].task_id == "t1"
    assert decisions[0].worker_id == "w1"
    assert t1.status == TaskState.QUEUED

    # Check that a worker lease was generated
    assert len(scheduler.leases) == 1
    lease = list(scheduler.leases.values())[0]
    assert lease.worker_id == "w1"
    assert lease.task_id == "t1"
    assert lease.status == "active"

    # Verify snapshot
    snapshot = scheduler.get_snapshot()
    assert snapshot.queue_length == 1  # t1 is queued
    assert snapshot.worker_count == 1
