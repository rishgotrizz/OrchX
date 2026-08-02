from typing import List, Union
from orchx_core.exceptions import CapabilityViolationError
from orchx_core.interfaces.plugin import BasePlugin
from orchx_runtime.context import KernelContext


class CapabilityEngine:
    """
    Validates execution privileges of plugins and agent task bindings.
    """

    def __init__(self, context: KernelContext) -> None:
        self.context = context

    def authorize_execution(self, plugin: BasePlugin, capability: str) -> None:
        """
        Verify if the given plugin possesses the specific capability.
        Raises CapabilityViolationError if the action is unauthorized.
        """
        # Register if not present in the capability registry
        if not self.context.capability_registry.is_registered(capability):
            self.context.capability_registry.register(capability)

        plugin_manifest = plugin.manifest
        
        # Check permissions list inside plugin manifest
        if capability not in plugin_manifest.capabilities and capability not in plugin_manifest.permissions:
            self.context.logger.warning(
                "Access violation: plugin %s does not declare capability %s",
                plugin_manifest.id,
                capability
            )
            raise CapabilityViolationError(
                f"Security policy violation: Plugin '{plugin_manifest.id}' does not possess capability '{capability}'."
            )

        self.context.logger.debug(
            "Access authorized for plugin %s and capability %s",
            plugin_manifest.id,
            capability
        )

    def verify_agent_permission(self, agent_id: str, tool_id: str) -> bool:
        """
        Check if an agent has the permissions required by a target tool.
        """
        agent = self.context.agent_registry.get(agent_id)
        tool = self.context.tool_registry.get(tool_id)

        if not agent or not tool:
            return False

        # Find overlapping permissions
        required_caps = tool.manifest.capabilities
        agent_permissions = agent.manifest.permissions

        for cap in required_caps:
            if cap not in agent_permissions:
                return False

        return True
