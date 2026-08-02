from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class MetricsTracker(ABC):
    """
    Decoupled interface for capturing numerical telemetry.
    """

    @abstractmethod
    def increment(self, name: str, value: float = 1.0, tags: Optional[Dict[str, str]] = None) -> None:
        """Increment a counter."""
        pass

    @abstractmethod
    def gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Record an absolute gauge value."""
        pass

    @abstractmethod
    def histogram(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Record a histogram value (latency distributions)."""
        pass


class TraceSpan(ABC):
    """
    Represents an active span context.
    """

    @abstractmethod
    def set_tag(self, key: str, value: str) -> None:
        pass

    @abstractmethod
    def finish(self) -> None:
        pass


class Tracer(ABC):
    """
    Decoupled interface for capturing distributed execution spans.
    """

    @abstractmethod
    def start_span(self, name: str, parent: Optional[TraceSpan] = None) -> TraceSpan:
        """Begin a tracing span."""
        pass


class ExecutionTimeline(ABC):
    """
    Decoupled trace logs specifically recording AI OS execution DAG steps.
    """

    @abstractmethod
    def record_step(self, execution_id: str, step_name: str, status: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Append task execution step timeline."""
        pass
