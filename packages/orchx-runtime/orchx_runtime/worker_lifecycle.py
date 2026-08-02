from typing import Dict, Set

from orchx_core.interfaces.worker import Worker, WorkerState


class WorkerLifecycleManager:
    """
    Validates state transition paths for registered workers.
    """

    ALLOWED_TRANSITIONS: Dict[WorkerState, Set[WorkerState]] = {
        WorkerState.OFFLINE: {WorkerState.STARTING},
        WorkerState.STARTING: {WorkerState.IDLE, WorkerState.FAILED},
        WorkerState.IDLE: {WorkerState.BUSY, WorkerState.DRAINING, WorkerState.STOPPED, WorkerState.FAILED},
        WorkerState.BUSY: {WorkerState.IDLE, WorkerState.DRAINING, WorkerState.FAILED},
        WorkerState.DRAINING: {WorkerState.STOPPED, WorkerState.FAILED},
        WorkerState.STOPPED: {WorkerState.STARTING, WorkerState.OFFLINE},
        WorkerState.FAILED: {WorkerState.STARTING, WorkerState.OFFLINE}
    }

    @classmethod
    def transition(cls, worker: Worker, next_state: WorkerState) -> None:
        """
        Transition worker status state, raising ValueError if the path is invalid.
        """
        current = worker.status
        if current == next_state:
            return

        valid_next = cls.ALLOWED_TRANSITIONS.get(current, set())
        if next_state not in valid_next:
            raise ValueError(
                f"Invalid worker state transition: Cannot transition worker '{worker.id}' "
                f"from state '{current.value}' to state '{next_state.value}'."
            )
        worker.status = next_state
        
        # Adjust status code based on states
        if next_state == WorkerState.BUSY:
            worker.current_load = 0.8
        elif next_state == WorkerState.IDLE:
            worker.current_load = 0.0
        elif next_state in (WorkerState.STOPPED, WorkerState.OFFLINE):
            worker.current_load = 0.0
