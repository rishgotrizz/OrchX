from typing import Dict, List, Optional
from orchx_core.interfaces.provider import BaseProvider


class ProviderRegistry:
    """
    Subsystem registry specifically managing loaded LLM providers.
    """

    def __init__(self) -> None:
        self._providers: Dict[str, BaseProvider] = {}

    def register(self, provider: BaseProvider) -> None:
        """Register an instantiated LLM provider plugin."""
        self._providers[provider.manifest.id] = provider

    def unregister(self, provider_id: str) -> Optional[BaseProvider]:
        """Remove a provider plugin from memory registry."""
        return self._providers.pop(provider_id, None)

    def get(self, provider_id: str) -> Optional[BaseProvider]:
        """Retrieve a specific LLM provider by ID."""
        return self._providers.get(provider_id)

    def list_all(self) -> List[BaseProvider]:
        """List all active LLM provider plugins."""
        return list(self._providers.values())
