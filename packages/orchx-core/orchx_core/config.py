from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class RuntimeConfig(BaseModel):
    """Core runtime engine configs."""
    environment: str = "development"
    plugin_dir: str = "plugins"
    heartbeat_interval_seconds: int = 10
    max_worker_tasks: int = 100


class SecurityConfig(BaseModel):
    """Security sandbox and authentication configuration variables."""
    secret_key: str
    token_expire_minutes: int = 60 * 24 * 7  # 1 week
    enable_sandbox: bool = True
    sandbox_user_id: Optional[int] = None
    rate_limit_calls_per_minute: int = 60


class ProviderConfig(BaseModel):
    """Adapter settings for individual API models."""
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    default_model: Optional[str] = None
    timeout_seconds: int = 30
    extra_settings: Dict[str, Any] = Field(default_factory=dict)


class KernelConfig(BaseModel):
    """Aggregate root configuration passed to the Kernel."""
    project_name: str = "OrchX"
    runtime: RuntimeConfig = Field(default_factory=RuntimeConfig)
    security: SecurityConfig
    providers: Dict[str, ProviderConfig] = Field(default_factory=dict)
    plugins: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    development: bool = True
