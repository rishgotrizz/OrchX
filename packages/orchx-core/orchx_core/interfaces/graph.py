from abc import ABC, abstractmethod
from typing import Dict, List, Any
from pydantic import BaseModel, Field

from orchx_core.interfaces.task import Task, Artifact
from orchx_core.interfaces.workflow import WorkflowDefinition, WorkflowInstance


class ExecutionGraph(BaseModel):
    """
    An immutable, directed acyclic graph (DAG) representing compiled execution tasks.
    Nodes hold concrete Task records, and Edges map step-level execution dependencies.
    
    Example:
        ExecutionGraph(
            workflow_instance_id="run-web-sass-104",
            nodes={"task-1": Task(...)},
            edges={"task-2": ["task-1"]} # task-2 depends on task-1
        )
    """
    workflow_instance_id: str = Field(..., description="Target execution run instance ID link")
    
    # Task mapping: task_id -> Task
    nodes: Dict[str, Task] = Field(default_factory=dict, description="Nodes of the DAG representing Task actions")
    
    # Dependency mapping: task_id -> list of sibling task_ids it directly depends on
    edges: Dict[str, List[str]] = Field(default_factory=dict, description="Directed dependency edges mapping execution order")
    
    # Registry of artifacts associated with this execution graph: artifact_id -> Artifact
    artifacts: Dict[str, Artifact] = Field(default_factory=dict, description="Registry of artifacts consumed or produced")

    def to_json(self) -> str:
        """Serialize the execution graph schema into standard JSON."""
        return self.model_dump_json(indent=2)

    def to_yaml(self) -> str:
        """Serialize the execution graph schema into standard YAML representation."""
        import yaml
        return yaml.dump(self.model_dump(), default_flow_style=False)


class WorkflowCompiler(ABC):
    """
    Decoupled compiler converting static workflow definitions into executable DAGs.
    Separated from execution scheduling.
    """

    @abstractmethod
    async def compile(
        self,
        definition: WorkflowDefinition,
        inputs: Dict[str, Any],
        instance_id: str
    ) -> ExecutionGraph:
        """
        Synthesize workflow steps and parameters into an immutable ExecutionGraph.
        """
        pass
