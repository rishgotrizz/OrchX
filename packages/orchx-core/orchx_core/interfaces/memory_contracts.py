from abc import ABC, abstractmethod
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class MemoryImportance(str, Enum):
    """Importance weights classification for prompt context prioritization."""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class MemoryRelationship(BaseModel):
    """
    directed link between memory objects, forming a traceable semantic graph.
    """
    source_id: str = Field(..., description="Origin memory object ID")
    target_id: str = Field(..., description="Target memory object ID")
    relationship_type: str = Field(
        ..., 
        description="Type: derives_from, references, updates, summarizes, replaces, contradicts"
    )


class MemoryProvenance(BaseModel):
    """
    Mandatory lineage tracing meta. Anonymous memories are strictly blocked.
    """
    memory_id: str
    source_execution_id: Optional[str] = None
    source_task_id: Optional[str] = None
    source_artifact_id: Optional[str] = None
    provider_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str = Field(..., description="e.g. 'agent-planner', 'developer'")
    project_id: str = Field(..., description="Binds memory to workspace context")
    session_id: str = Field(..., description="Binds memory to conversation run thread")


class MemoryObject(BaseModel):
    """
    Base contract for all OrchX memory structures.
    """
    id: str = Field(..., description="Unique memory identifier")
    content: str = Field(..., description="Semantic content payload")
    provenance: MemoryProvenance = Field(..., description="Mandatory audit path")
    importance: MemoryImportance = Field(MemoryImportance.NORMAL)
    relationships: List[MemoryRelationship] = Field(default_factory=list)
    version: int = Field(1, description="Incrementing version count")
    expires_at: Optional[datetime] = Field(None, description="Optional timestamp for automatic archiving")
    metadata: Dict[str, Any] = Field(default_factory=dict)


# Logical memory layers
class WorkingMemory(MemoryObject):
    """Short-lived runtime execution context variables."""
    pass


class SessionMemory(MemoryObject):
    """Current active user/conversation session logs."""
    pass


class ProjectMemory(MemoryObject):
    """Persistent project records (specs, graph execution logs)."""
    pass


class KnowledgeMemory(MemoryObject):
    """Long-term reusable knowledge across multiple workspaces."""
    pass


class ContextBudget(BaseModel):
    """
    Budget constraint parameters utilized when compiling prompts.
    """
    maximum_tokens: int = Field(4096, description="Max token allocation limit")
    maximum_memory_objects: int = Field(10, description="Max memory nodes limit")
    prioritization_strategy: str = Field("recency", description="Sort parameter: recency, importance")
    compression_strategy: str = Field("truncate", description="Budget action: truncate, none")


class RetrievalStrategy(ABC):
    """
    Abstract interface for search indexing strategies.
    """

    @abstractmethod
    def retrieve(self, query: str, memories: List[MemoryObject]) -> List[MemoryObject]:
        """Resolves matching memory candidates for a prompt search query."""
        pass
