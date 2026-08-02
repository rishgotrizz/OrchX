from typing import Dict, List, Optional
from orchx_core.interfaces.agent import BaseAgent


class AgentRegistry:
    """
    Subsystem registry specifically managing loaded AI agents.
    """

    def __init__(self) -> None:
        self._agents: Dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent) -> None:
        """Register an instantiated agent plugin."""
        self._agents[agent.manifest.id] = agent

    def unregister(self, agent_id: str) -> Optional[BaseAgent]:
        """Remove an agent plugin from memory registry."""
        return self._agents.pop(agent_id, None)

    def get(self, agent_id: str) -> Optional[BaseAgent]:
        """Retrieve a specific agent by ID."""
        return self._agents.get(agent_id)

    def list_all(self) -> List[BaseAgent]:
        """List all active agent plugins."""
        return list(self._agents.values())
