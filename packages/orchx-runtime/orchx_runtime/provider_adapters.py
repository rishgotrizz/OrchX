import asyncio
import time
import uuid
import httpx
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, AsyncGenerator

from orchx_core.interfaces.provider_contracts import (
    BaseProvider,
    Provider,
    Model,
    ProviderRequest,
    ProviderResponse,
    ProviderHealth,
    UsageMetrics,
)
from orchx_runtime.infrastructure_layer import ProviderCredentialManager
from orchx_runtime.transport import TransportLayer
from orchx_runtime.billing import BillingEngine
from orchx_runtime.formatters import RequestFormatterFactory
from orchx_runtime.normalizers import ResponseNormalizerFactory
from orchx_runtime.provider_metadata import ProviderMetadataRegistry

class BaseRealProvider(BaseProvider):
    """
    Live HTTP adapter base class implementing decoupled transport, formatting, and billing.
    """
    def __init__(self, provider_id: str, cred_manager: ProviderCredentialManager, metadata_registry: ProviderMetadataRegistry):
        self.provider_id = provider_id
        self.metadata = metadata_registry.get(provider_id)
        if not self.metadata:
            raise ValueError(f"Provider {provider_id} not found in metadata registry.")
            
        self._info = Provider(id=provider_id, name=self.metadata.display_name, status="online")
        self._models = [Model(id=m, name=m, provider_id=provider_id, capabilities=self.metadata.supported_capabilities) for m in self.metadata.default_models]
        
        self.cred_manager = cred_manager
        
        # Instantiate decoupled subsystems based on strategy
        self.transport = TransportLayer()
        self.formatter = RequestFormatterFactory.get_formatter(self.metadata.discovery_strategy)
        self.normalizer = ResponseNormalizerFactory.get_normalizer(self.metadata.discovery_strategy)
        self.billing = BillingEngine()
        
        # Cached properties
        self.latency = 0.0
        self.last_success = None
        self.last_error = None
        
        # We start a model discovery async task or wait for first call
        self._models_fetched = False

    @property
    def failure_flag(self) -> bool:
        return self.transport.circuit_breaker.state == "open"
        
    @failure_flag.setter
    def failure_flag(self, value: bool):
        if value:
            self.transport.circuit_breaker.state = "open"
        else:
            self.transport.circuit_breaker.state = "closed"

    @property
    def provider_info(self) -> Provider:
        return self._info

    def list_models(self) -> List[Model]:
        return self._models
        
    async def _fetch_models(self):
        # Extremely simplified discovery using discovery_strategy endpoints
        if self._models_fetched or not self.metadata.model_discovery_endpoint:
            return
            
        key = self.cred_manager.get_credential(self._info.id) if self.metadata.authentication_required else ""
        headers = self._build_headers(key)
        url = self.metadata.base_url + self.metadata.model_discovery_endpoint
        
        try:
            resp, _ = await self.transport.execute("GET", url, headers=headers)
            data = resp.json()
            if self.metadata.discovery_strategy == "openai-v1":
                new_models = []
                for m in data.get("data", []):
                    new_models.append(Model(id=m["id"], name=m["id"], provider_id=self.provider_id, capabilities=self.metadata.supported_capabilities))
                if new_models:
                    self._models = new_models
            elif self.metadata.discovery_strategy == "ollama-tags":
                new_models = []
                for m in data.get("models", []):
                    new_models.append(Model(id=m["name"], name=m["name"], provider_id=self.provider_id, capabilities=self.metadata.supported_capabilities))
                if new_models:
                    self._models = new_models
            self._models_fetched = True
        except Exception:
            pass # Silent fail fallback to defaults

    async def get_health(self) -> ProviderHealth:
        await self._fetch_models()
        return ProviderHealth(
            provider_id=self._info.id,
            provider_name=self._info.name,
            status=self._info.status if self.transport.circuit_breaker.state == "closed" else "degraded",
            latency=self.latency,
            availability=1.0 if self.transport.circuit_breaker.state == "closed" else 0.0,
            last_success=self.last_success,
            last_error=self.last_error,
            supported_models=[m.id for m in self._models],
            circuit_breaker_status=self.transport.circuit_breaker.state,
            failure_rate=0.0,
            capability_source="live" if self._models_fetched else "registry",
            retry_count=0
        )

    def _build_headers(self, key: str) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if not self.metadata.authentication_required:
            return headers
            
        if self.metadata.authentication_method == "Bearer":
            headers["Authorization"] = f"Bearer {key}"
        elif self.metadata.authentication_method == "x-api-key":
            headers["x-api-key"] = key
        elif self.metadata.authentication_method == "api-key":
            headers["api-key"] = key
        return headers

    async def call(self, request: ProviderRequest) -> ProviderResponse:
        await self._fetch_models()
        
        model = next((m for m in self._models if m.id == request.model_id), None)
        if not model:
            # Fallback in case discovery hasn't picked it up but user requested it
            model = Model(id=request.model_id, name=request.model_id, provider_id=self.provider_id)
            
        key = self.cred_manager.get_credential(self._info.id) if self.metadata.authentication_required else ""
        headers = self._build_headers(key)
        
        url = self.metadata.base_url + self.metadata.chat_endpoint
        payload = self.formatter.format(request, model)
        payload["stream"] = False # Override for non-streaming
        
        try:
            resp, telemetry = await self.transport.execute("POST", url, headers=headers, json=payload)
            self.last_success = datetime.now(timezone.utc)
            self.latency = telemetry["total_duration"]
            
            provider_resp = self.normalizer.normalize(resp.json(), model)
            
            # Enrich telemetry
            provider_resp.usage.latency_ms = telemetry["total_duration"]
            provider_resp.usage.retry_count = telemetry["retry_count"]
            provider_resp.usage.http_status = telemetry["http_status"]
            
            # Billing
            self.billing.record_usage(self.provider_id, model, provider_resp.usage)
            
            return provider_resp
        except Exception as e:
            self.last_error = str(e)
            raise

    async def stream(self, request: ProviderRequest) -> AsyncGenerator[ProviderResponse, None]:
        await self._fetch_models()
        
        model = next((m for m in self._models if m.id == request.model_id), None)
        if not model:
            model = Model(id=request.model_id, name=request.model_id, provider_id=self.provider_id)
            
        key = self.cred_manager.get_credential(self._info.id)
        headers = self._build_headers(key)
        
        url = self.metadata.base_url + self.metadata.chat_endpoint
        payload = self.formatter.format(request, model)
        payload["stream"] = True
        
        try:
            accumulated_usage = UsageMetrics()
            async for chunk, telemetry in self.transport.stream("POST", url, headers=headers, json=payload):
                self.latency = telemetry["total_duration"]
                
                partial_resp = self.normalizer.parse_stream_chunk(chunk, model)
                if partial_resp:
                    # Update billing
                    if partial_resp.usage and partial_resp.usage.total_tokens > 0:
                        accumulated_usage = partial_resp.usage
                        accumulated_usage.latency_ms = telemetry["total_duration"]
                        accumulated_usage.first_byte_latency = telemetry["first_byte_time"]
                        
                    yield partial_resp
                    
            if accumulated_usage.total_tokens > 0:
                self.billing.record_usage(self.provider_id, model, accumulated_usage)
                
            self.last_success = datetime.now(timezone.utc)
        except Exception as e:
            self.last_error = str(e)
            raise


# Dynamically exposing class names expected by older tests/managers
# We just route them to the new unified base with their static IDs
class OpenAIProviderAdapter(BaseRealProvider):
    def __init__(self, cred_manager: ProviderCredentialManager, metadata_registry: ProviderMetadataRegistry = None):
        super().__init__("openai", cred_manager, metadata_registry or ProviderMetadataRegistry())

class AnthropicProviderAdapter(BaseRealProvider):
    def __init__(self, cred_manager: ProviderCredentialManager, metadata_registry: ProviderMetadataRegistry = None):
        super().__init__("anthropic", cred_manager, metadata_registry or ProviderMetadataRegistry())

class GoogleGeminiProviderAdapter(BaseRealProvider):
    def __init__(self, cred_manager: ProviderCredentialManager, metadata_registry: ProviderMetadataRegistry = None):
        super().__init__("gemini", cred_manager, metadata_registry or ProviderMetadataRegistry())

class OpenRouterProviderAdapter(BaseRealProvider):
    def __init__(self, cred_manager: ProviderCredentialManager, metadata_registry: ProviderMetadataRegistry = None):
        super().__init__("openrouter", cred_manager, metadata_registry or ProviderMetadataRegistry())

class OllamaProviderAdapter(BaseRealProvider):
    def __init__(self, cred_manager: ProviderCredentialManager, metadata_registry: ProviderMetadataRegistry = None):
        super().__init__("ollama", cred_manager, metadata_registry or ProviderMetadataRegistry())

class GroqProviderAdapter(BaseRealProvider):
    def __init__(self, cred_manager: ProviderCredentialManager, metadata_registry: ProviderMetadataRegistry = None):
        super().__init__("groq", cred_manager, metadata_registry or ProviderMetadataRegistry())

class KimiProviderAdapter(BaseRealProvider):
    def __init__(self, cred_manager: ProviderCredentialManager, metadata_registry: ProviderMetadataRegistry = None):
        super().__init__("kimi", cred_manager, metadata_registry or ProviderMetadataRegistry())

class NvidiaNimProviderAdapter(BaseRealProvider):
    def __init__(self, cred_manager: ProviderCredentialManager, metadata_registry: ProviderMetadataRegistry = None):
        super().__init__("nvidia", cred_manager, metadata_registry or ProviderMetadataRegistry())
