from abc import abstractmethod
from typing import Any, Dict
from orchx_core.interfaces.plugin import BasePlugin


class BaseTool(BasePlugin):
    """
    Plugin contract for tools that can be bound to LLM function calls.
    """

    @property
    @abstractmethod
    def parameter_schema(self) -> Dict[str, Any]:
        """JSON Schema defining parameters this tool expects."""
        pass

    @abstractmethod
    async def execute(self, **kwargs: Any) -> Dict[str, Any]:
        """Execute the tool function logic."""
        pass
