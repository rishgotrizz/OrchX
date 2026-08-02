from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, EmailStr, ConfigDict


# User Schemas
class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Auth Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    exp: Optional[int] = None


# Audit Log Schemas
class AuditLogBase(BaseModel):
    action: str
    details: Optional[Dict[str, Any]] = None


class AuditLogResponse(AuditLogBase):
    id: int
    user_id: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Simplified Plugin Telemetry schemas
class DashboardPluginInfo(BaseModel):
    id: str
    name: str
    version: str
    api_version: str
    type: str
    capabilities: List[str]
    permissions: List[str]


class DashboardStatsResponse(BaseModel):
    status: str
    version: str
    uptime: float
    loaded_components: List[str]
    capabilities: List[str]
    providers_count: int
    agents_count: int
    tools_count: int
    workflows_count: int
    recent_logs: List[AuditLogResponse]
