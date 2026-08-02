from abc import ABC, abstractmethod
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ReviewCategory(str, Enum):
    """Structured categories for code and task reviews."""
    CORRECTNESS = "correctness"
    SECURITY = "security"
    PERFORMANCE = "performance"
    MAINTAINABILITY = "maintainability"
    ARCHITECTURE = "architecture"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    STYLE = "style"


class ReviewSeverity(str, Enum):
    """Standardized finding impact severities."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ReviewEvidence(BaseModel):
    """
    Mandatory proof details explaining why a finding was flagged.
    """
    artifact_id: str = Field(..., description="Target reviewed artifact / run ID")
    file_path: str = Field(..., description="Target file path under inspection")
    location: str = Field(..., description="Location context, e.g. line numbers range 'L10-L15'")
    snippet: str = Field(..., description="Code snippet snippet or parameter context")
    explanation: str = Field(..., description="Detailed explanation of the issue")


class SuggestedFix(BaseModel):
    """
    Optional recommendation to remedy the reported finding. Read-only.
    """
    description: str
    rationale: str
    confidence: float = Field(0.0, description="Confidence score from 0.0 to 1.0")
    affected_artifacts: List[str] = Field(default_factory=list)


class ReviewFinding(BaseModel):
    """
    A single reported issue generated during code analysis.
    """
    id: str = Field(..., description="Unique finding UUID")
    category: ReviewCategory
    severity: ReviewSeverity
    message: str
    evidence: ReviewEvidence = Field(..., description="Mandatory detailed proof payload")
    suggested_fix: Optional[SuggestedFix] = None


class ReviewRuleMetadata(BaseModel):
    """
    Static metadata identifying a pluggable validation rule.
    """
    rule_id: str
    name: str
    version: str = Field("0.1.0")
    category: ReviewCategory
    description: str
    enabled: bool = True


class ReviewReport(BaseModel):
    """
    Immutable review report consolidating findings and scores.
    """
    review_id: str
    target_id: str = Field(..., description="Target ID reviewed")
    findings: List[ReviewFinding] = Field(default_factory=list)
    summary: str
    overall_score: float = Field(100.0, description="Overall score rating from 0.0 to 100.0")
    severity_breakdown: Dict[ReviewSeverity, int] = Field(default_factory=dict)
    total_findings: int = 0
    passed_rules: List[str] = Field(default_factory=list)
    failed_rules: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    reviewed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ReviewRule(ABC):
    """
    Abstract base class for pluggable validation rules.
    """

    @property
    @abstractmethod
    def metadata(self) -> ReviewRuleMetadata:
        pass

    @abstractmethod
    def evaluate(self, content: str, target_name: str) -> List[ReviewFinding]:
        """Runs the rule logic and yields any found issues."""
        pass
