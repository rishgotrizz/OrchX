from typing import Dict, List, Optional
from orchx_core.interfaces.worker import Worker


class WorkerRegistry:
    """
    Subsystem registry managing active Worker metadata profiles.
    """

    def __init__(self) -> None:
        self._workers: Dict[str, Worker] = {}

    def register(self, worker: Worker) -> None:
        """Register an active worker descriptor."""
        self._workers[worker.id] = worker

    def unregister(self, worker_id: str) -> Optional[Worker]:
        """Remove a worker registration."""
        return self._workers.pop(worker_id, None)

    def get(self, worker_id: str) -> Optional[Worker]:
        """Retrieve a specific worker profile."""
        return self._workers.get(worker_id)

    def list_all(self) -> List[Worker]:
        """List active worker registrations."""
        return list(self._workers.values())
