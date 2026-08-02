from typing import Any, Dict, List, Optional, Tuple
from orchx_core.interfaces.task import Task, TaskPriority
from orchx_core.interfaces.worker import Worker
from orchx_core.interfaces.scheduler import SchedulingPolicy


class BaseMatchingPolicy(SchedulingPolicy):
    """
    Shared matching logic validating capability and resource requirements.
    """

    def verify_compatibility(self, task: Task, worker: Worker) -> Tuple[bool, Dict[str, bool]]:
        checks = {
            "task_type_supported": task.type in worker.supported_task_types,
            "capabilities_supported": all(cap in worker.capabilities for cap in task.required_capabilities),
            "cpu_sufficient": task.resources.cpu_cores <= worker.available_resources.cpu_cores,
            "memory_sufficient": task.resources.memory_mb <= worker.available_resources.memory_mb,
            "gpu_sufficient": task.resources.gpu_count <= worker.available_resources.gpu_count,
            "disk_sufficient": task.resources.temp_disk_mb <= worker.available_resources.temp_disk_mb,
        }

        # Check environment constraints
        constraints_satisfied = True
        for constraint in task.constraints:
            # We check metadata on the worker to match constraints
            val = worker.version if constraint.key == "version" else str(worker.available_resources.model_dump().get(constraint.key, ""))
            if constraint.operator == "==" and val != constraint.value:
                constraints_satisfied = False
                break

        checks["constraints_satisfied"] = constraints_satisfied
        compatible = all(checks.values())
        return compatible, checks


from typing import Tuple

class FIFOPolicy(BaseMatchingPolicy):
    """Orders tasks by creation sequence, matching first available worker."""

    def sort_queue(self, queue: List[Task]) -> List[Task]:
        # Preserve original order
        return queue

    def select_worker(self, task: Task, workers: List[Worker]) -> Optional[Worker]:
        for worker in workers:
            if worker.status == "offline" or worker.current_load >= 1.0:
                continue
            compatible, _ = self.verify_compatibility(task, worker)
            if compatible:
                return worker
        return None


class PriorityPolicy(BaseMatchingPolicy):
    """Orders tasks based on priority weights: CRITICAL > HIGH > MEDIUM > LOW."""

    def sort_queue(self, queue: List[Task]) -> List[Task]:
        priority_weights = {
            TaskPriority.CRITICAL: 4,
            TaskPriority.HIGH: 3,
            TaskPriority.MEDIUM: 2,
            TaskPriority.LOW: 1
        }
        return sorted(queue, key=lambda t: priority_weights.get(t.priority, 2), reverse=True)

    def select_worker(self, task: Task, workers: List[Worker]) -> Optional[Worker]:
        # Out of compatible workers, select the one with the lowest load
        compatible_workers = []
        for worker in workers:
            if worker.status == "offline" or worker.current_load >= 1.0:
                continue
            compatible, _ = self.verify_compatibility(task, worker)
            if compatible:
                compatible_workers.append(worker)
        
        if not compatible_workers:
            return None

        # Sort by load to assign to least utilized worker
        return sorted(compatible_workers, key=lambda w: w.current_load)[0]
