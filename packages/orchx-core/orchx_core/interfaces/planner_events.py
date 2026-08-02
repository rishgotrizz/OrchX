from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class PlannerEvent(BaseModel):
    """Base event structure for all planner state updates."""
    id: str
    topic: str
    timestamp: float
    payload: Dict[str, Any] = Field(default_factory=dict)
