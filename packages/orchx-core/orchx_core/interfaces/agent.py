from abc import abstractmethod
from typing import Any, List, Optional
from orchx_core.interfaces.plugin import BasePlugin
from orchx_core.interfaces.provider import BaseProvider
from orchx_core.interfaces.tool import BaseTool


class BaseAgent(BasePlugin):
    """
    Plugin contract for specialised agents.
    """

    @abstractmethod
    async def run_task(
        self,
        task_description: str,
        tools: List[BaseTool],
        provider: BaseProvider,
        context: Optional[dict] = None,
        **kwargs: Any
    ) -> str:
        """Run the agent specialized loop on a given task description."""
        pass
        
    @property
    @abstractmethod
    def capabilities_required(self) -> List[str]:
        """List of tool capabilities this agent requires to execute."""
        pass
