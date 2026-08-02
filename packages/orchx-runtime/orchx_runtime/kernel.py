import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from orchx_core.exceptions import CapabilityViolationError
from orchx_core.interfaces.event import Event
from orchx_core.interfaces.health import HealthExposed, HealthStatus
from orchx_core.version import __version__ as core_version
from orchx_runtime.context import KernelContext
from orchx_runtime.loader import PluginLoader
from orchx_runtime.suggestion_engine import SuggestionRegistry, SuggestionEngine


class Kernel(HealthExposed):
    """
    The permanent foundation and orchestrator container for OrchX.
    Manages runtime services, plugin registry, and async event dispatch routing.
    """

    def __init__(self, context: KernelContext) -> None:
        self.context = context
        self.loader = PluginLoader(context)
        self._boot_time: Optional[float] = None
        self._is_active = False
        self._last_error: Optional[str] = None
        
        self.suggestion_registry = SuggestionRegistry()
        self.suggestion_engine = SuggestionEngine(self.context.event_bus, self.suggestion_registry)
        self.context.register_service("suggestion_registry", self.suggestion_registry)
        self.context.register_service("suggestion_engine", self.suggestion_engine)
        
        # Double Verification System - Phase 2 (Runtime)
        from orchx_core.architecture.validator import ArchitectureConsistencyValidator
        validator = ArchitectureConsistencyValidator()
        validator._validate_implementations()
        if len(validator.errors) > 0:
            raise ValueError(f"Runtime Architecture Validation Failed:\n" + "\n".join(validator.errors))

    async def start(self) -> None:
        """
        Boot the kernel and trigger startup lifecycle hooks on all registered plugins.
        """
        self.context.logger.info("Initializing OrchX Kernel Subsystems...")
        self._boot_time = time.time()
        self._is_active = True

        # Load plugins from the configured plugins folder path
        plugin_dir = self.context.config.runtime.plugin_dir
        await self.loader.load_from_directory(plugin_dir)

        # Start SuggestionEngine
        await self.suggestion_engine.start()

        # Trigger start lifecycle hook for all loaded plugins
        all_plugins = self._get_all_plugin_instances()
        for plugin in all_plugins:
            try:
                await plugin.start(self.context)
            except Exception as e:
                self._last_error = f"Failed to start plugin '{plugin.manifest.id}': {e}"
                self.context.logger.error("Plugin failed startup hook", plugin_id=plugin.manifest.id, error=str(e))

        self.context.logger.info("OrchX Kernel online and active.")

    async def stop(self) -> None:
        """
        Gracefully stop the kernel runtime, triggering stop lifecycle hooks on all plugins.
        """
        self.context.logger.info("Shutting down OrchX Kernel...")
        self._is_active = False

        # Stop SuggestionEngine
        await self.suggestion_engine.stop()

        all_plugins = self._get_all_plugin_instances()
        for plugin in all_plugins:
            try:
                await plugin.stop(self.context)
            except Exception as e:
                self.context.logger.error("Plugin failed shutdown hook", plugin_id=plugin.manifest.id, error=str(e))

        self.context.logger.info("OrchX Kernel offline.")

    async def dispatch_event(self, event: Event) -> None:
        """
        Inject an event packet into the central event bus.
        """
        await self.context.event_bus.publish(event)

    async def run_task(self, agent_id: str, task_description: str, **kwargs: Any) -> str:
        """
        Coordinate execution of a task via a specific agent.
        Validates capabilities before executing.
        """
        agent = self.context.agent_registry.get(agent_id)
        if not agent:
            raise ValueError(f"Agent '{agent_id}' is not registered.")

        # Find first compatible provider
        providers = self.context.provider_registry.list_all()
        if not providers:
            raise ValueError("No providers registered to complete this task execution.")
        provider = providers[0]

        # Fetch tools that match the agent's permission profile
        all_tools = self.context.tool_registry.list_all()
        authorized_tools = []
        for tool in all_tools:
            # Match capabilities required by the tool with permissions granted to the agent
            tool_caps = tool.manifest.capabilities
            is_authorized = True
            for cap in tool_caps:
                if cap not in agent.manifest.permissions:
                    is_authorized = False
                    break
            if is_authorized:
                authorized_tools.append(tool)

        self.context.logger.info(
            "Executing task",
            agent_id=agent_id,
            provider_id=provider.manifest.id,
            authorized_tools_count=len(authorized_tools)
        )

        # Dispatch execution event
        await self.dispatch_event(
            Event(
                id=f"evt-{int(time.time())}",
                topic="task.started",
                payload={"agent_id": agent_id, "task": task_description}
            )
        )

        try:
            result = await agent.run_task(
                task_description=task_description,
                tools=authorized_tools,
                provider=provider,
                context={"kernel_context": self.context},
                **kwargs
            )

            await self.dispatch_event(
                Event(
                    id=f"evt-{int(time.time())}",
                    topic="task.completed",
                    payload={"agent_id": agent_id, "status": "success"}
                )
            )
            return result
        except Exception as e:
            self._last_error = f"Task execution failed on agent '{agent_id}': {e}"
            await self.dispatch_event(
                Event(
                    id=f"evt-{int(time.time())}",
                    topic="task.failed",
                    payload={"agent_id": agent_id, "error": str(e)}
                )
            )
            raise e

    def health(self) -> HealthStatus:
        """
        Retrieve state indicators and active registry details.
        """
        status = "healthy"
        if self._last_error:
            status = "degraded"
        if not self._is_active:
            status = "unhealthy"

        uptime = 0.0
        if self._boot_time:
            uptime = time.time() - self._boot_time

        loaded_components = [
            f"provider:{p.manifest.id}" for p in self.context.provider_registry.list_all()
        ] + [
            f"agent:{a.manifest.id}" for a in self.context.agent_registry.list_all()
        ] + [
            f"tool:{t.manifest.id}" for t in self.context.tool_registry.list_all()
        ]

        return HealthStatus(
            status=status,
            version=core_version,
            uptime=uptime,
            loaded_components=loaded_components,
            last_error=self._last_error,
            capabilities=self.context.capability_registry.list_all(),
            details={
                "providers_count": len(self.context.provider_registry.list_all()),
                "agents_count": len(self.context.agent_registry.list_all()),
                "tools_count": len(self.context.tool_registry.list_all()),
                "workflows_count": len(self.context.workflow_registry.list_all())
            }
        )

    def _get_all_plugin_instances(self) -> List[Any]:
        """Aggregate list of all registered plugin objects."""
        return (
            list(self.context.provider_registry.list_all()) +
            list(self.context.agent_registry.list_all()) +
            list(self.context.tool_registry.list_all())
        )
