from typing import Dict, List, Optional, Any


class TaskTypeRegistry:
    """
    Subsystem registry tracking permitted task execution types.
    """

    def __init__(self) -> None:
        self._types: Dict[str, Dict[str, Any]] = {}

    def register(self, type_name: str, schema: Dict[str, Any]) -> None:
        """Register a valid task type and its expected input/output schema metadata."""
        self._types[type_name] = schema

    def unregister(self, type_name: str) -> Optional[Dict[str, Any]]:
        """Remove a task type registration."""
        return self._types.pop(type_name, None)

    def get(self, type_name: str) -> Optional[Dict[str, Any]]:
        """Retrieve task type specifications."""
        return self._types.get(type_name)

    def list_all(self) -> List[str]:
        """List all permitted task types."""
        return list(self._types.keys())
