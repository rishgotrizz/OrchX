from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class EngineeringMemoryEntry(BaseModel):
    """
    Immutable historical engineering knowledge record tracking evidence stats.
    """
    entry_id: str
    entry_type: str = Field(..., description="e.g. 'architecture', 'lesson', 'report'")
    content: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(0.5, description="Confidence rating from 0.0 to 1.0")
    evidence_count: int = Field(0)
    successful_projects: int = Field(0)
    failed_projects: int = Field(0)
    last_validated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ArchitectureGenome(BaseModel):
    """
    Reusable canonical service building block specification.
    """
    genome_id: str = Field(..., description="e.g. 'auth', 'payments', 'notifications'")
    purpose: str
    responsibilities: List[str] = Field(default_factory=list)
    required_capabilities: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    implementation_patterns: List[str] = Field(default_factory=list)
    security_patterns: List[str] = Field(default_factory=list)
    testing_patterns: List[str] = Field(default_factory=list)
    deployment_considerations: str


class EngineeringPrinciple(BaseModel):
    """
    A foundational design principle used to validate and score design candidates.
    """
    id: str = Field(..., description="e.g. 'plugin_first', 'security_first'")
    name: str
    description: str
    weight: float = Field(1.0, description="Weight modifier from 0.0 to 2.0")


class Pattern(BaseModel):
    """
    Structured reusable implementation pattern descriptor.
    """
    id: str
    category: str = Field(..., description="Architectural, Backend, Frontend, etc.")
    intent: str
    applicability: str
    tradeoffs: List[str] = Field(default_factory=list)
    anti_patterns: List[str] = Field(default_factory=list)
    implementation_guidance: str


class AntiPattern(BaseModel):
    """
    Known poor coding or design structures flagged during analysis reviews.
    """
    id: str = Field(..., description="e.g. 'god_object', 'circular_dependency'")
    name: str
    description: str
    remedy: str


class EngineeringRecommendation(BaseModel):
    """
    Advisory recommendation derived from engineering knowledge.
    """
    id: str
    recommendation_type: str = Field(..., description="e.g. 'reuse_genome', 'avoid_antipattern'")
    description: str
    confidence: float
    governing_principle_id: Optional[str] = None


class EngineeringKnowledgeReport(BaseModel):
    """
    Consolidated report summarizing structural patterns and rule conformities.
    """
    report_id: str
    summary: str
    genomes_count: int = 0
    patterns_evaluated: int = 0
    anti_patterns_flagged: int = 0
    principles_compliance_average: float = 0.0
    recommendations: List[EngineeringRecommendation] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
