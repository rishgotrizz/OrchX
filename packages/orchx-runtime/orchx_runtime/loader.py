import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any

from orchx_core.exceptions import PluginLoadError
from orchx_core.interfaces.plugin import PluginManifest, BasePlugin
from orchx_core.interfaces.provider import BaseProvider
from orchx_core.interfaces.agent import BaseAgent
from orchx_core.interfaces.tool import BaseTool
from orchx_core.version import __version__ as core_version
from orchx_runtime.context import KernelContext


def check_version_compatibility(core_ver: str, plugin_api_ver: str) -> bool:
    """
    Returns True if the plugin's requested api_version is semver-compatible with core.
    For simplicity, compatibility is confirmed if major versions match.
    """
    try:
        c_parts = core_ver.split(".")
        p_parts = plugin_api_ver.split(".")
        
        # Major version match
        if c_parts[0] == p_parts[0]:
            return True
    except Exception:
        pass
    return False


class PluginLoader:
    """
    Discovers, validates manifests, dynamically imports, and manages lifecycle transitions for plugins.
    """

    def __init__(self, context: KernelContext) -> None:
        self.context = context

    async def load_from_directory(self, plugin_dir: str) -> None:
        """
        Scan a folder structure for subdirectories containing a manifest.json.
        """
        dir_path = Path(plugin_dir)
        if not dir_path.exists():
            self.context.logger.warning("Plugin scanner target directory not found: %s", str(dir_path))
            dir_path.mkdir(parents=True, exist_ok=True)
            return

        self.context.logger.info("Scanning directory for plugin manifests: %s", str(dir_path))

        for entry in os.scandir(dir_path):
            if entry.is_dir():
                manifest_path = Path(entry.path) / "manifest.json"
                if manifest_path.exists():
                    try:
                        await self.load_plugin(manifest_path)
                    except Exception as e:
                        self.context.logger.error(
                            "Safe load failed: Plugin did not boot in %s: %s",
                            entry.name,
                            str(e)
                        )

    async def load_plugin(self, manifest_file: Path) -> BasePlugin:
        """
        Load, validate, instantiate, and execute initial lifecycle triggers for a plugin.
        """
        try:
            with open(manifest_file, "r") as f:
                data = json.load(f)
            
            manifest = PluginManifest(**data)
        except Exception as e:
            raise PluginLoadError(f"Malformed manifest JSON in {manifest_file}: {e}")

        # Check API version compatibility
        if not check_version_compatibility(core_version, manifest.api_version):
            raise PluginLoadError(
                f"Plugin '{manifest.id}' requires API version '{manifest.api_version}', "
                f"which is incompatible with current Core version '{core_version}'."
            )

        # Dynamic import class entry point
        try:
            # Add plugin directory to python search path for relative imports
            plugin_root = str(manifest_file.parent)
            if plugin_root not in sys.path:
                sys.path.insert(0, plugin_root)

            # Resolve module and class name (e.g., "my_plugin.module.MyClass")
            parts = manifest.entrypoint.split(".")
            module_name = ".".join(parts[:-1])
            class_name = parts[-1]

            # Import module
            module = importlib.import_module(module_name)
            plugin_class = getattr(module, class_name)

            if not issubclass(plugin_class, BasePlugin):
                raise PluginLoadError(f"Entrypoint class '{class_name}' must inherit from BasePlugin.")

            # Instantiate plugin with manifest config
            plugin_instance = plugin_class(manifest)

            # Run INITIAL lifecycles
            await plugin_instance.install(self.context)
            await plugin_instance.initialize(self.context)

            # Register with appropriate registries
            if manifest.type == "provider" and isinstance(plugin_instance, BaseProvider):
                self.context.provider_registry.register(plugin_instance)
            elif manifest.type == "agent" and isinstance(plugin_instance, BaseAgent):
                self.context.agent_registry.register(plugin_instance)
            elif manifest.type == "tool" and isinstance(plugin_instance, BaseTool):
                self.context.tool_registry.register(plugin_instance)
            else:
                raise PluginLoadError(
                    f"Plugin '{manifest.id}' declared type '{manifest.type}' "
                    f"which does not match its implemented subclass."
                )

            # Register capability permissions
            for cap in manifest.capabilities:
                self.context.capability_registry.register(cap)
            for perm in manifest.permissions:
                self.context.capability_registry.register(perm)

            self.context.logger.info("Successfully loaded plugin %s (type: %s)", manifest.id, manifest.type)
            return plugin_instance

        except Exception as e:
            self.context.logger.error("Failed loading module class %s: %s", manifest.entrypoint, str(e))
            raise PluginLoadError(f"Plugin load sequence failed for '{manifest.id}': {e}") from e
