from enum import Enum
from typing import Any, List, Optional
from pydantic import BaseModel, Field

class SuggestionPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Suggestion(BaseModel):
    id: str = Field(..., description="Unique identifier for the suggestion")
    priority: SuggestionPriority = Field(..., description="Priority of the suggestion")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    source: str = Field(..., description="Source of the suggestion")
    reasoning: str = Field(..., description="Reasoning behind the suggestion")
    affected_components: List[str] = Field(default_factory=list, description="List of components affected")
    estimated_impact: str = Field(..., description="Estimated impact of implementing this suggestion")
    payload: Optional[Any] = Field(None, description="Optional additional data for this suggestion")
