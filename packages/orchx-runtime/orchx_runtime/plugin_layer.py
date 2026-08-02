import uuid
from typing import Any, Dict, List, Optional
from orchx_core.interfaces.plugin_contracts import (
    PluginManifest,
    PluginLifecycleState,
    PluginTrustProfile,
    PluginHealthReport,
    PluginSelectionPolicy,
    PluginDependencyLock,
    PluginAuditRecord,
    CapabilityMetrics,
    PluginCompatibilityMatrix
)
from orchx_core.interfaces.agent_contracts import AgentSandboxPermissions

class PluginRegistry:
    """Manages the index of all discovered and installed plugins."""
    def __init__(self) -> None:
        self.plugins: Dict[str, PluginManifest] = {}
        self.plugin_states: Dict[str, PluginLifecycleState] = {}
        self.trust_profiles: Dict[str, PluginTrustProfile] = {}
        
    def register_plugin(self, manifest: PluginManifest, state: PluginLifecycleState = PluginLifecycleState.DISCOVERED) -> None:
        self.plugins[manifest.plugin_id] = manifest
        self.plugin_states[manifest.plugin_id] = state
        self.trust_profiles[manifest.plugin_id] = PluginTrustProfile(plugin_id=manifest.plugin_id)
        
    def get_plugins_providing(self, capability: str) -> List[PluginManifest]:
        return [p for p in self.plugins.values() if capability in p.capabilities_provided]

class CapabilityVirtualizer:
    """Maps abstract capabilities to concrete plugins using the selection policy."""
    def __init__(self, registry: PluginRegistry, policy: PluginSelectionPolicy):
        self.registry = registry
        self.policy = policy
        
    def resolve_capability(self, capability: str) -> Optional[PluginManifest]:
        candidates = self.registry.get_plugins_providing(capability)
        
        # Filter by compatibility (e.g., must be INSTALLED/ENABLED and healthy/trusted)
        valid_candidates = []
        for c in candidates:
            state = self.registry.plugin_states.get(c.plugin_id)
            trust = self.registry.trust_profiles.get(c.plugin_id)
            if state in [PluginLifecycleState.ENABLED, PluginLifecycleState.RUNNING]:
                if not self.policy.prioritize_security_trust or (trust and trust.reputation >= self.policy.require_minimum_reputation):
                    valid_candidates.append((c, trust))
                    
        if not valid_candidates:
            return None
            
        # Sort by reputation
        valid_candidates.sort(key=lambda x: x[1].reputation if x[1] else 0, reverse=True)
        return valid_candidates[0][0]

class PluginDependencyResolver:
    """Resolves dependencies and generates dependency locks."""
    def __init__(self, registry: PluginRegistry):
        self.registry = registry
        
    def resolve_and_lock(self, plugin_id: str) -> PluginDependencyLock:
        manifest = self.registry.plugins.get(plugin_id)
        if not manifest:
            raise ValueError("Plugin not found")
            
        resolved = {}
        # Naive resolution for testing
        for dep in manifest.plugin_dependencies:
            dep_plugin = self.registry.plugins.get(dep)
            if not dep_plugin:
                raise ValueError(f"Missing dependency: {dep}")
            resolved[dep] = dep_plugin.version
            
        return PluginDependencyLock(
            plugin_id=plugin_id,
            version=manifest.version,
            resolved_dependencies=resolved
        )

class PluginRuntime:
    """Handles lifecycle state transitions and audit trailing."""
    def __init__(self, registry: PluginRegistry):
        self.registry = registry
        self.audit_log: List[PluginAuditRecord] = []
        self.history: Dict[str, List[PluginManifest]] = {}
        
    def _audit(self, plugin_id: str, action: str, details: str) -> None:
        self.audit_log.append(PluginAuditRecord(
            event_id=str(uuid.uuid4()),
            plugin_id=plugin_id,
            action=action,
            details=details
        ))
        
    def enable_plugin(self, plugin_id: str) -> bool:
        if plugin_id in self.registry.plugins:
            # Compatibility matrix validation should happen here against kernel version.
            # Assuming kernel is valid for this mock.
            self.registry.plugin_states[plugin_id] = PluginLifecycleState.ENABLED
            self._audit(plugin_id, "ENABLE", "Plugin enabled successfully")
            return True
        return False
        
    def rollback_plugin(self, plugin_id: str) -> bool:
        if plugin_id in self.history and len(self.history[plugin_id]) > 1:
            # Revert to previous manifest
            prev = self.history[plugin_id][-2]
            self.registry.plugins[plugin_id] = prev
            self.history[plugin_id].pop()
            self._audit(plugin_id, "ROLLBACK", f"Rolled back to {prev.version}")
            return True
        return False

class PluginSandboxManager:
    """Determines the effective permission intersection."""
    def get_effective_permissions(self, agent_perms: AgentSandboxPermissions, plugin_manifest: PluginManifest) -> List[str]:
        # Effective permission is intersection of what agent allows and what plugin requests
        agent_allowed_tools = set(agent_perms.allowed_tools)
        plugin_requested = set(plugin_manifest.permissions_requested)
        # Security Policy overrides not modeled here but implicitly checked by SecurityLayer.
        return list(agent_allowed_tools.intersection(plugin_requested))

class PluginHealthManager:
    """Monitors plugin health endpoints and logs reports."""
    def check_health(self, plugin_id: str) -> PluginHealthReport:
        # Mock health check
        return PluginHealthReport(
            plugin_id=plugin_id,
            status="healthy"
        )

class InternalMarketplace:
    """Distributes plugin manifests."""
    def __init__(self) -> None:
        self.available_plugins: List[PluginManifest] = []
        
    def publish_internal(self, manifest: PluginManifest) -> None:
        self.available_plugins.append(manifest)
