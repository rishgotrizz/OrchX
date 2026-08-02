from typing import Any, Dict, List, Optional


class WorkflowRegistry:
    """
    Subsystem registry managing workflow contracts and definitions.
    """

    def __init__(self) -> None:
        self._workflows: Dict[str, Any] = {}

    def register(self, workflow_id: str, workflow_definition: Any) -> None:
        """Register a workflow configuration schema."""
        self._workflows[workflow_id] = workflow_definition

    def unregister(self, workflow_id: str) -> Optional[Any]:
        """Remove a workflow specification."""
        return self._workflows.pop(workflow_id, None)

    def get(self, workflow_id: str) -> Optional[Any]:
        """Retrieve a registered workflow."""
        return self._workflows.get(workflow_id)

    def list_all(self) -> List[str]:
        """List all registered workflow IDs."""
        return list(self._workflows.keys())
