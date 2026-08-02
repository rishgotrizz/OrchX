from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# 1. Enums
class OptimizationProfile(str, Enum):
    SPEED = "speed"
    QUALITY = "quality"
    BALANCED = "balanced"
    LOWEST_COST = "lowest_cost"
    FREE_ONLY = "free_only"
    MAXIMUM_SECURITY = "maximum_security"
    MAXIMUM_RELIABILITY = "maximum_reliability"
    CREATIVE = "creative"


class OptimizationObjective(str, Enum):
    QUALITY = "quality"
    COST = "cost"
    LATENCY = "latency"
    RELIABILITY = "reliability"
    SECURITY = "security"
    RESOURCE_USAGE = "resource_usage"
    ENERGY_EFFICIENCY = "energy_efficiency"


# 2. Telemetry, Benchmarks & Histories
class ExecutionTelemetry(BaseModel):
    """
    Immutable telemetry summarizing resources consumed by a finished execution context.
    """
    execution_id: str
    workflow_id: str
    task_count: int
    provider: str
    model: str
    worker: str
    optimization_profile: OptimizationProfile = Field(OptimizationProfile.BALANCED)
    execution_duration: float
    queue_wait_time: float
    review_score: float
    security_score: float
    token_usage: int
    estimated_cost: float
    retry_count: int
    success: bool
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BenchmarkEntry(BaseModel):
    """
    Consolidated performance metrics recorded for a specific provider model setup.
    """
    provider: str
    model: str
    workflow_type: str
    task_type: str
    latency: float
    cost: float
    review_score: float
    security_score: float
    success_rate: float
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ModelPerformanceHistory(BaseModel):
    """
    Rolling statistical average metrics compiled over multiple benchmark runs.
    """
    provider: str
    model: str
    execution_count: int
    average_latency: float
    average_cost: float
    average_review_score: float
    average_security_score: float
    average_success_rate: float
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# 3. Recommendations & Reports
class Recommendation(BaseModel):
    """Advisory recommendation outlining expected metric changes."""
    id: str
    recommendation_type: str = Field(..., description="e.g. 'model_swap', 'retrieval_swap'")
    description: str
    confidence: float = Field(..., description="Rating from 0.0 to 1.0")
    expected_quality_change: float = Field(0.0, description="Estimated change in review score")
    expected_latency_change: float = Field(0.0, description="Estimated change in latency seconds")
    expected_cost_change: float = Field(0.0, description="Estimated change in cost USD")
    expected_reliability_change: float = Field(0.0, description="Estimated change in success rate")


class OptimizationReport(BaseModel):
    """Advisory report consolidating recommendations and predicted improvements."""
    report_id: str
    optimization_profile: OptimizationProfile
    benchmark_summary: Dict[str, Any] = Field(default_factory=dict)
    execution_summary: Dict[str, Any] = Field(default_factory=dict)
    recommendations: List[Recommendation] = Field(default_factory=list)
    estimated_improvements: Dict[str, float] = Field(default_factory=dict)
    confidence: float = 1.0
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# 4. Canonical Replay fingerprint
class ExecutionDNA(BaseModel):
    """
    Immutable fingerprint tying together all execution data logs for future replay/tuning.
    """
    dna_id: str
    execution_id: str
    execution_report_id: str
    review_report_id: Optional[str] = None
    security_report_id: Optional[str] = None
    telemetry: ExecutionTelemetry
    optimization_report_id: Optional[str] = None
    memory_references: List[str] = Field(default_factory=list)
    produced_artifacts: List[str] = Field(default_factory=list)
    provider_usage: Dict[str, Any] = Field(default_factory=dict)
    timeline: List[Dict[str, Any]] = Field(default_factory=list)


# 5. System Subsystem Metrics
class SystemMetrics(BaseModel):
    kernel_metrics: Dict[str, Any] = Field(default_factory=dict)
    scheduler_metrics: Dict[str, Any] = Field(default_factory=dict)
    worker_metrics: Dict[str, Any] = Field(default_factory=dict)
    provider_metrics: Dict[str, Any] = Field(default_factory=dict)
    memory_metrics: Dict[str, Any] = Field(default_factory=dict)
    review_metrics: Dict[str, Any] = Field(default_factory=dict)
    security_metrics: Dict[str, Any] = Field(default_factory=dict)
    optimization_metrics: Dict[str, Any] = Field(default_factory=dict)
