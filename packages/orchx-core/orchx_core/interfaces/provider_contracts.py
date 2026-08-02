from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field


class Model(BaseModel):
    """
    Metadata describing an AI model exposed by a Provider.
    Includes capability flags and pricing parameters.
    """
    id: str = Field(..., description="Unique model identifier, e.g. 'gpt-4o'")
    name: str = Field(..., description="Human-friendly model name")
    provider_id: str = Field(..., description="Parent provider ID")
    capabilities: List[str] = Field(default_factory=list, description="Capabilities e.g. 'chat', 'vision', 'tool_calling'")
    cost_per_million_prompt: float = Field(0.0, description="Cost in USD per 1M prompt tokens")
    cost_per_million_completion: float = Field(0.0, description="Cost in USD per 1M completion tokens")
    status: str = Field("online", description="Model status: online, offline")


class Provider(BaseModel):
    """
    Metadata representation of an AI provider.
    """
    id: str = Field(..., description="Unique provider ID e.g. 'openai'")
    name: str = Field(..., description="Human name e.g. 'OpenAI'")
    status: str = Field("online", description="Provider status: online, degraded, offline")


class ProviderHealth(BaseModel):
    """
    Auditing metadata capturing the latency, error logs, and availability of a provider.
    """
    provider_id: str
    provider_name: str
    status: str = Field("online", description="online, degraded, offline")
    latency: float = Field(0.0, description="Recent request latency in seconds")
    availability: float = Field(1.0, description="Fraction of successful checks from 0.0 to 1.0")
    last_success: Optional[datetime] = None
    last_error: Optional[str] = None
    supported_models: List[str] = Field(default_factory=list)
    quota_information: Optional[Dict[str, Any]] = None
    circuit_breaker_status: str = Field("closed", description="closed, open, half-open")
    failure_rate: float = Field(0.0, description="Rate of request failures")
    capability_source: str = Field("registry", description="registry or live")
    retry_count: int = Field(0, description="Number of times requests were retried recently")


class UsageMetrics(BaseModel):
    """
    Normalized token usage, cost processing metrics, and latencies returned by any provider.
    """
    prompt_tokens: int = Field(0)
    completion_tokens: int = Field(0)
    cached_tokens: int = Field(0, description="Tokens retrieved from cache if supported by provider")
    total_tokens: int = Field(0)
    latency_ms: float = Field(0.0, description="Total API request latency in milliseconds")
    estimated_cost: float = Field(0.0, description="Estimated total cost of the request in USD")
    provider_processing_time: float = Field(0.0, description="Internal provider processing time in milliseconds")
    
    # Advanced Telemetry
    dns_lookup_time: float = Field(0.0)
    tcp_connection_time: float = Field(0.0)
    tls_handshake_time: float = Field(0.0)
    first_byte_latency: float = Field(0.0)
    first_token_latency: float = Field(0.0)
    stream_duration: float = Field(0.0)
    total_duration: float = Field(0.0)
    tokens_per_second: float = Field(0.0)
    retry_count: int = Field(0)
    http_status: int = Field(200)
    error_classification: Optional[str] = None


class ProviderRequest(BaseModel):
    """
    Normalized provider-agnostic LLM completion request schema.
    """
    model_id: str = Field(..., description="Target model ID")
    messages: List[Dict[str, str]] = Field(..., description="Messages list containing role and content keys")
    temperature: float = Field(0.7)
    max_tokens: int = Field(2048)
    tools: List[Dict[str, Any]] = Field(default_factory=list, description="Tool definitions schemas")
    response_format: Optional[Dict[str, Any]] = None


class ProviderResponse(BaseModel):
    """
    Normalized provider-agnostic completion response.
    """
    id: str = Field(..., description="Unique completion request ID")
    content: Optional[str] = None
    role: str = Field("assistant")
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list)
    usage: UsageMetrics = Field(default_factory=UsageMetrics)
    model_used: str = Field(..., description="Actual model ID utilized")
    finish_reason: str = Field("stop")


class BaseProvider(ABC):
    """
    Abstract interface for interchangeable provider client adapters.
    """

    @property
    @abstractmethod
    def provider_info(self) -> Provider:
        pass

    @abstractmethod
    def list_models(self) -> List[Model]:
        pass

    @abstractmethod
    async def call(self, request: ProviderRequest) -> ProviderResponse:
        pass
        
    @abstractmethod
    async def stream(self, request: ProviderRequest): # -> AsyncGenerator[ProviderResponse, None]
        """Yields partial ProviderResponse objects for streaming."""
        pass

    @abstractmethod
    async def get_health(self) -> ProviderHealth:
        pass


class ProviderSelectionStrategy(ABC):
    """
    pluggable strategy interface to select the correct model & provider.
    """

    @abstractmethod
    def select_model(
        self,
        required_capabilities: List[str],
        providers: List[BaseProvider]
    ) -> Optional[Tuple[BaseProvider, Model]]:
        """Resolves target provider and model based on capability matches."""
        pass
