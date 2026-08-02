from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from orchx_core.interfaces.task import Task
from orchx_core.interfaces.worker import Worker
from orchx_core.interfaces.graph import ExecutionGraph


class SchedulingDecision(BaseModel):
    """
    Observability record tracing a single scheduling resolution.
    Strictly read-only; does not modify execution graph routes.
    """
    task_id: str
    worker_id: str
    scheduling_policy: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    decision_reason: str
    constraint_checks: Dict[str, bool] = Field(default_factory=dict)
    resource_summary: Dict[str, Any] = Field(default_factory=dict)


class SchedulerSnapshot(BaseModel):
    """
    Read-only snapshot of the Scheduler queue states and utilization.
    """
    queue_length: int
    ready_tasks: List[str] = Field(default_factory=list)
    blocked_tasks: List[str] = Field(default_factory=list)
    running_tasks: List[str] = Field(default_factory=list)
    completed_tasks: List[str] = Field(default_factory=list)
    worker_count: int
    active_policy: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SchedulingPolicy(ABC):
    """
    Pluggable sorting and assignment strategy.
    """

    @abstractmethod
    def sort_queue(self, queue: List[Task]) -> List[Task]:
        """Re-orders the list of executable ready tasks."""
        pass

    @abstractmethod
    def select_worker(self, task: Task, workers: List[Worker]) -> Optional[Worker]:
        """Selects a compatible worker based on constraint matching rules."""
        pass


class Scheduler(ABC):
    """
    Central Coordinator managing worker registration and queue state resolutions.
    """

    @abstractmethod
    def register_worker(self, worker: Worker) -> None:
        pass

    @abstractmethod
    def unregister_worker(self, worker_id: str) -> Optional[Worker]:
        pass

    @abstractmethod
    async def tick(self) -> List[SchedulingDecision]:
        """Evaluates graph dependencies and dispatches ready tasks to workers."""
        pass

    @abstractmethod
    def get_snapshot(self) -> SchedulerSnapshot:
        pass
