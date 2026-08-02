from typing import Dict, List, Optional
from orchx_core.interfaces.tool import BaseTool


class ToolRegistry:
    """
    Subsystem registry specifically managing loaded tool bindings.
    """

    def __init__(self) -> None:
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """Register an instantiated tool plugin."""
        self._tools[tool.manifest.id] = tool

    def unregister(self, tool_id: str) -> Optional[BaseTool]:
        """Remove a tool plugin from memory registry."""
        return self._tools.pop(tool_id, None)

    def get(self, tool_id: str) -> Optional[BaseTool]:
        """Retrieve a specific tool by ID."""
        return self._tools.get(tool_id)

    def list_all(self) -> List[BaseTool]:
        """List all active tool plugins."""
        return list(self._tools.values())
