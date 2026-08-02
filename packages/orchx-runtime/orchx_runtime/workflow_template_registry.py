from typing import Dict, List, Optional
from orchx_core.interfaces.workflow import WorkflowDefinition


class WorkflowTemplateRegistry:
    """
    Subsystem registry managing defined workflow templates.
    """

    def __init__(self) -> None:
        self._templates: Dict[str, WorkflowDefinition] = {}

    def register(self, template: WorkflowDefinition) -> None:
        """Register a static workflow template."""
        self._templates[template.id] = template

    def unregister(self, template_id: str) -> Optional[WorkflowDefinition]:
        """Remove a template."""
        return self._templates.pop(template_id, None)

    def get(self, template_id: str) -> Optional[WorkflowDefinition]:
        """Retrieve a workflow template."""
        return self._templates.get(template_id)

    def list_all(self) -> List[WorkflowDefinition]:
        """List all active templates."""
        return list(self._templates.values())
