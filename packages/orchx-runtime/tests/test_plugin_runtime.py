import pytest
from orchx_core.interfaces.plugin_contracts import (
    PluginManifest,
    PluginLifecycleState,
    PluginSelectionPolicy
)
from orchx_core.interfaces.agent_contracts import AgentSandboxPermissions
from orchx_runtime.plugin_layer import (
    PluginRegistry,
    CapabilityVirtualizer,
    PluginDependencyResolver,
    PluginRuntime,
    PluginSandboxManager
)

def test_capability_virtualization():
    registry = PluginRegistry()
    
    # Register Playwright Plugin
    p1 = PluginManifest(
        plugin_id="playwright-plugin", name="Playwright", version="1.0", author="OrchX", description="",
        capabilities_provided=["browser", "e2e_testing"]
    )
    registry.register_plugin(p1, PluginLifecycleState.ENABLED)
    registry.trust_profiles["playwright-plugin"].reputation = 95.0
    
    # Register Puppeteer Plugin
    p2 = PluginManifest(
        plugin_id="puppeteer-plugin", name="Puppeteer", version="1.0", author="OrchX", description="",
        capabilities_provided=["browser"]
    )
    registry.register_plugin(p2, PluginLifecycleState.ENABLED)
    registry.trust_profiles["puppeteer-plugin"].reputation = 85.0
    
    policy = PluginSelectionPolicy(require_minimum_reputation=80.0)
    virtualizer = CapabilityVirtualizer(registry, policy)
    
    selected = virtualizer.resolve_capability("browser")
    assert selected is not None
    # Should pick Playwright because of higher reputation
    assert selected.plugin_id == "playwright-plugin"

def test_plugin_dependency_resolution():
    registry = PluginRegistry()
    p1 = PluginManifest(plugin_id="p-core", name="Core", version="1.0", author="", description="")
    p2 = PluginManifest(plugin_id="p-ext", name="Ext", version="1.0", author="", description="", plugin_dependencies=["p-core"])
    
    registry.register_plugin(p1)
    registry.register_plugin(p2)
    
    resolver = PluginDependencyResolver(registry)
    lock = resolver.resolve_and_lock("p-ext")
    assert lock.plugin_id == "p-ext"
    assert "p-core" in lock.resolved_dependencies
    assert lock.resolved_dependencies["p-core"] == "1.0"
    
    # Missing dependency test
    p3 = PluginManifest(plugin_id="p-broken", name="Broken", version="1.0", author="", description="", plugin_dependencies=["p-missing"])
    registry.register_plugin(p3)
    with pytest.raises(ValueError):
        resolver.resolve_and_lock("p-broken")

def test_plugin_sandbox_permissions():
    agent_perms = AgentSandboxPermissions(allowed_tools=["network_read", "fs_read", "fs_write"])
    plugin = PluginManifest(
        plugin_id="p1", name="", version="", author="", description="",
        permissions_requested=["network_read", "network_write", "fs_read"]
    )
    
    sandbox_manager = PluginSandboxManager()
    effective = sandbox_manager.get_effective_permissions(agent_perms, plugin)
    
    assert "network_read" in effective
    assert "fs_read" in effective
    assert "network_write" not in effective
    assert "fs_write" not in effective

def test_plugin_rollback_and_audit():
    registry = PluginRegistry()
    runtime = PluginRuntime(registry)
    
    p_v1 = PluginManifest(plugin_id="p1", name="", version="1.0", author="", description="")
    p_v2 = PluginManifest(plugin_id="p1", name="", version="2.0", author="", description="")
    
    registry.register_plugin(p_v1)
    runtime.history["p1"] = [p_v1]
    
    # Update to v2
    registry.plugins["p1"] = p_v2
    runtime.history["p1"].append(p_v2)
    runtime._audit("p1", "UPDATE", "Updated to v2")
    
    assert registry.plugins["p1"].version == "2.0"
    
    # Rollback to v1
    success = runtime.rollback_plugin("p1")
    assert success is True
    assert registry.plugins["p1"].version == "1.0"
    
    # Check audit log
    assert len(runtime.audit_log) == 2
    assert runtime.audit_log[1].action == "ROLLBACK"
