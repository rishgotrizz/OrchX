from typing import Dict, List, Optional
from orchx_core.interfaces.graph import ExecutionGraph


class ExecutionGraphRegistry:
    """
    Subsystem registry managing active compiled execution graphs.
    """

    def __init__(self) -> None:
        self._graphs: Dict[str, ExecutionGraph] = {}

    def register(self, graph: ExecutionGraph) -> None:
        """Register a compiled execution graph."""
        self._graphs[graph.workflow_instance_id] = graph

    def unregister(self, instance_id: str) -> Optional[ExecutionGraph]:
        """Remove a graph instance from registry."""
        return self._graphs.pop(instance_id, None)

    def get(self, instance_id: str) -> Optional[ExecutionGraph]:
        """Retrieve execution graph details."""
        return self._graphs.get(instance_id)

    def list_all(self) -> List[ExecutionGraph]:
        """List active compiled graph runs."""
        return list(self._graphs.values())
