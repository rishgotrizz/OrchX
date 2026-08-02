from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class HealthStatus(BaseModel):
    """
    Standard state telemetry for any subsystem.
    """
    status: str  # "healthy" | "degraded" | "unhealthy"
    version: str
    uptime: float  # Seconds
    loaded_components: List[str]
    last_error: Optional[str] = None
    capabilities: List[str] = []
    details: Dict[str, Any] = {}


class HealthExposed(ABC):
    """
    Subsystem interface that reports health data.
    """

    @abstractmethod
    def health(self) -> HealthStatus:
        """Query state and compile telemetry."""
        pass
