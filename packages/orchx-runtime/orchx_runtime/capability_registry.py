from typing import Dict, List, Set


class CapabilityRegistry:
    """
    Subsystem registry managing active capability scopes.
    """

    def __init__(self) -> None:
        self._capabilities: Set[str] = set()

    def register(self, capability: str) -> None:
        """Register a new capability string token, e.g. 'filesystem.read'."""
        self._capabilities.add(capability)

    def unregister(self, capability: str) -> None:
        """Remove a capability token."""
        self._capabilities.discard(capability)

    def list_all(self) -> List[str]:
        """List all active capabilities registered in the kernel."""
        return sorted(list(self._capabilities))

    def is_registered(self, capability: str) -> bool:
        """Check if a capability string is registered."""
        return capability in self._capabilities
