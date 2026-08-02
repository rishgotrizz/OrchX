from abc import ABC, abstractmethod
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field


# 1. Enums
class SecurityProfile(str, Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"
    ENTERPRISE = "enterprise"
    PARANOID = "paranoid"


class SecurityZone(str, Enum):
    PUBLIC = "public"
    PROJECT = "project"
    TRUSTED = "trusted"
    SENSITIVE = "sensitive"
    CRITICAL = "critical"


class RiskLevel(str, Enum):
    MINIMAL = "minimal"     # 0-20
    LOW = "low"             # 21-40
    MODERATE = "moderate"   # 41-60
    HIGH = "high"           # 61-80
    CRITICAL = "critical"   # 81-100


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


# 2. Permissions, Trust & Risk Models
class PermissionSet(BaseModel):
    """Declared permissions for workers, plugins, or tool tasks."""
    filesystem: List[str] = Field(default_factory=list, description="filesystem e.g. ['read', 'write']")
    network: List[str] = Field(default_factory=list, description="network e.g. ['github.com', 'api.openai.com']")
    provider: List[str] = Field(default_factory=list, description="authorized providers e.g. ['openai', 'gemini']")
    memory: List[str] = Field(default_factory=list, description="authorized memory layers e.g. ['working', 'session']")
    shell: bool = Field(False, description="Whether direct shell access is enabled")


class TrustScore(BaseModel):
    """Dynamic trust parameters verified across execution registries."""
    score: float = Field(100.0, description="Verification trust rating from 0.0 to 100.0")
    confidence: float = Field(1.0, description="Confidence weighting from 0.0 to 1.0")
    last_validation: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    reason: str = Field("Verified baseline identity signature")


class RiskAssessment(BaseModel):
    """
    Structured explainable risk assessment generated before human approvals.
    """
    overall_risk_score: float = Field(0.0, description="Overall risk rating from 0 to 100")
    risk_level: RiskLevel = Field(RiskLevel.MINIMAL)
    confidence: float = Field(1.0)
    affected_assets: List[str] = Field(default_factory=list)
    affected_permissions: List[str] = Field(default_factory=list)
    policies_triggered: List[str] = Field(default_factory=list)
    required_permissions: List[str] = Field(default_factory=list)
    potential_consequences: List[str] = Field(default_factory=list)
    mitigation_recommendations: List[str] = Field(default_factory=list)
    estimated_recovery_difficulty: str = Field("low")
    risk_formula_breakdown: str = Field(
        ..., 
        description="Explainable breakdown: Base Risk + Permission + Environment + Trust + Network + Sensitive"
    )


# 3. Human Approval Framework
class ApprovalRequest(BaseModel):
    """Human approval record containing the mandatory risk assessment."""
    request_id: str
    operation_name: str
    target_asset_id: str
    requested_by: str
    risk_assessment: RiskAssessment = Field(..., description="Mandatory RiskAssessment packet")
    status: ApprovalStatus = Field(ApprovalStatus.PENDING)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ApprovalDecision(BaseModel):
    decision_id: str
    request_id: str
    approver: str
    decision: str = Field(..., description="approve or reject")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    comment: Optional[str] = None


class ApprovalRecord(BaseModel):
    request: ApprovalRequest
    decision: Optional[ApprovalDecision] = None


# 4. Security Audits & Decision Logs
class SecurityDecision(BaseModel):
    """Immutable audit entry tracking RuntimeGuard decisions."""
    decision_id: str
    execution_id: str
    evaluated_policies: List[str] = Field(default_factory=list)
    evaluated_permissions: List[str] = Field(default_factory=list)
    trust_scores: Dict[str, float] = Field(default_factory=dict)
    approval_state: str = Field("allowed")
    final_decision: str = Field("Allow", description="Allow or Deny")
    explanation: str = Field(..., description="Transparent reason detailing why decision was made")


class SecurityAuditRecord(BaseModel):
    """Immutable security audit log record."""
    actor: str
    action: str
    target: str
    policy: str
    decision: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    reason: str


class SecurityReport(BaseModel):
    """Consolidated security analysis report."""
    report_id: str
    findings: List[Dict[str, Any]] = Field(default_factory=list)
    trust_score: float = 100.0
    risk_score: float = 0.0
    violated_policies: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PluginManifest(BaseModel):
    """Supply chain verification descriptors."""
    signature: str
    checksum: str
    version: str
    author: str
    publisher: str
    permissions: PermissionSet
    integrity_hash: str


# 5. Abstract Base Interfaces
class SecretVault(ABC):
    """Abstract interface for secure secrets vaults."""

    @abstractmethod
    async def get_secret(self, key: str) -> Optional[str]:
        pass

    @abstractmethod
    async def store_secret(self, key: str, value: str) -> None:
        pass


class SecurityPolicy(ABC):
    """Abstract base class for security validation policies."""

    @property
    @abstractmethod
    def policy_name(self) -> str:
        pass

    @abstractmethod
    def validate(self, context: Any) -> Tuple[bool, str]:
        """Evaluates compliance for context. Returns (passed, explanation)."""
        pass
