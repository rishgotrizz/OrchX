from abc import ABC, abstractmethod
from typing import Dict, List, Set, TypeVar

T = TypeVar("T")


class DependencyNode(ABC):
    """Represents a node inside an execution DAG."""

    @property
    @abstractmethod
    def id(self) -> str:
        pass


class DependencyGraph(ABC):
    """
    Contracts managing Directed Acyclic Graphs (DAGs) of items.
    """

    @abstractmethod
    def add_node(self, node_id: str, data: Any = None) -> None:
        """Add node to graph."""
        pass

    @abstractmethod
    def add_dependency(self, node_id: str, depends_on_id: str) -> None:
        """Add directed edge between node_id -> depends_on_id."""
        pass

    @abstractmethod
    def get_dependencies(self, node_id: str) -> List[str]:
        """List direct dependencies."""
        pass

    @abstractmethod
    def has_cycles(self) -> bool:
        """Verify whether graph contains circular dependencies."""
        pass

    @abstractmethod
    def get_topological_order(self) -> List[str]:
        """Compute topological sort of node execution order."""
        pass
