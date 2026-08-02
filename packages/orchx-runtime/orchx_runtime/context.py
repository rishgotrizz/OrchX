import logging
from typing import Any, Dict
from orchx_core.config import KernelConfig
from orchx_core.interfaces.event import EventBus
from orchx_core.interfaces.observability import MetricsTracker
from orchx_runtime.agent_registry import AgentRegistry
from orchx_runtime.capability_registry import CapabilityRegistry
from orchx_runtime.provider_registry import ProviderRegistry
from orchx_runtime.tool_registry import ToolRegistry
from orchx_runtime.workflow_registry import WorkflowRegistry


class SilentMetricsTracker(MetricsTracker):
    """Fallback no-op metrics tracker."""
    def increment(self, name: str, value: float = 1.0, tags: Dict[str, str] = None) -> None: pass
    def gauge(self, name: str, value: float, tags: Dict[str, str] = None) -> None: pass
    def histogram(self, name: str, value: float, tags: Dict[str, str] = None) -> None: pass


class KernelContext:
    """
    Context container injected into all runtime services and plugins to avoid global state.
    """

    def __init__(
        self,
        config: KernelConfig,
        event_bus: EventBus,
        provider_registry: ProviderRegistry,
        agent_registry: AgentRegistry,
        tool_registry: ToolRegistry,
        workflow_registry: WorkflowRegistry,
        capability_registry: CapabilityRegistry,
        logger: Any = None,
        metrics: MetricsTracker = None,
    ) -> None:
        self.config = config
        self.event_bus = event_bus
        self.provider_registry = provider_registry
        self.agent_registry = agent_registry
        self.tool_registry = tool_registry
        self.workflow_registry = workflow_registry
        self.capability_registry = capability_registry
        
        self.logger = logger or logging.getLogger("orchx")
        self.metrics = metrics or SilentMetricsTracker()
        
        # Extensible services container
        self._services: Dict[str, Any] = {}

    def register_service(self, name: str, service: Any) -> None:
        """Register a dynamic utility service to avoid breaking API consumers."""
        self._services[name] = service

    def get_service(self, name: str) -> Any:
        """Retrieve a registered utility service."""
        return self._services.get(name)
