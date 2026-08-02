from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class PluginManifest(BaseModel):
    """
    Decoupled specifications manifest required for every loadable OrchX Plugin.
    """
    id: str = Field(..., description="Unique machine-readable identifier, e.g. 'openai-provider'")
    name: str = Field(..., description="Human-readable plugin name")
    version: str = Field(..., description="Semantic version of the plugin, e.g. '1.0.0'")
    api_version: str = Field(..., description="Required minimum core api version, e.g. '0.1.0'")
    type: str = Field(..., description="Plugin type classifier: 'provider', 'agent', or 'tool'")
    description: Optional[str] = None
    author: Optional[str] = None
    capabilities: List[str] = Field(default_factory=list, description="Capabilities this plugin offers")
    permissions: List[str] = Field(default_factory=list, description="Capabilities/permissions this plugin requests access to")
    dependencies: List[str] = Field(default_factory=list, description="Other plugin IDs this plugin depends on")
    configuration_schema: Dict[str, Any] = Field(default_factory=dict, description="JSON Schema for configuration options")
    entrypoint: str = Field(..., description="Full Python import path of the plugin entrypoint class, e.g. 'my_plugin.MyClass'")


class BasePlugin(ABC):
    """
    Abstract Base Class that all OrchX plugins (Providers, Agents, Tools) must subclass.
    Defines the standard asynchronous execution lifecycle hooks.
    """

    def __init__(self, manifest: PluginManifest) -> None:
        self.manifest = manifest

    @abstractmethod
    async def install(self, context: Any) -> None:
        """Executed once when the plugin is first installed in the system environment."""
        pass

    @abstractmethod
    async def initialize(self, context: Any) -> None:
        """Executed during engine boot. Set up local directories or configurations."""
        pass

    @abstractmethod
    async def start(self, context: Any) -> None:
        """Activate executing loops or subscription handlers."""
        pass

    @abstractmethod
    async def pause(self, context: Any) -> None:
        """Temporarily pause work execution."""
        pass

    @abstractmethod
    async def resume(self, context: Any) -> None:
        """Resume work execution from paused state."""
        pass

    @abstractmethod
    async def stop(self, context: Any) -> None:
        """Gracefully release open connections or resources."""
        pass

    @abstractmethod
    async def uninstall(self, context: Any) -> None:
        """Executed when the plugin is removed from the system environment."""
        pass
