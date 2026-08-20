from typing import Any, Dict, List, Optional, Tuple

from orchx_core.interfaces.provider_contracts import (
    BaseProvider,
    Model,
    ProviderRequest,
    ProviderResponse,
    ProviderSelectionStrategy,
)
from orchx_runtime.selection_strategies import DefaultSelectionStrategy
from orchx_core.exceptions import (
    NoProviderConfiguredError,
    ProviderAuthFailedError,
    ProviderUnavailableError,
    ProviderTimeoutError,
    ProviderRequestFailedError,
)


class ProviderManager:
    """
    Gateway coordinating AI provider routing, pluggable selectors, 
    timeouts retry, and fallback failovers.
    """

    def __init__(self, default_strategy: Optional[ProviderSelectionStrategy] = None) -> None:
        self.default_strategy = default_strategy or DefaultSelectionStrategy()
        self._providers: List[BaseProvider] = []
        self.metrics = {
            "request_started": 0,
            "request_completed": 0,
            "request_failed": 0,
            "failover_count": 0
        }

    def register_provider(self, provider: BaseProvider) -> None:
        """Register a client provider adapter."""
        self._providers.append(provider)

    def unregister_provider(self, provider_id: str) -> Optional[BaseProvider]:
        """Remove a provider adapter registration."""
        for p in self._providers:
            if p.provider_info.id == provider_id:
                self._providers.remove(p)
                return p
        return None

    def list_providers(self) -> List[BaseProvider]:
        """List active provider adapters."""
        return self._providers

    async def execute_request(
        self,
        required_capabilities: List[str],
        messages: List[Dict[str, str]],
        strategy: Optional[ProviderSelectionStrategy] = None
    ) -> ProviderResponse:
        """
        Executes a prompt against compatible registered provider models,
        monitoring and recovering from faults dynamically.
        """
        active_strategy = strategy or self.default_strategy
        self.metrics["request_started"] += 1

        # Copy providers list for fallback exclusions on outage
        eligible_providers = list(self._providers)

        while True:
            # 1. Resolve compatible model
            selection = active_strategy.select_model(required_capabilities, eligible_providers)
            if not selection:
                self.metrics["request_failed"] += 1
                has_any_configured = any(getattr(p, "has_credentials", False) for p in self._providers)
                if not has_any_configured:
                    raise NoProviderConfiguredError()
                raise ProviderUnavailableError(
                    provider="all",
                    message="Outage resolution failed: No online provider models satisfy capabilities."
                )

            provider, model = selection
            request = ProviderRequest(
                model_id=model.id,
                messages=messages
            )

            try:
                # 2. Call normalized request
                response = await provider.call(request)
                self.metrics["request_completed"] += 1
                return response
            except TimeoutError as e:
                provider.failure_flag = True
                self.metrics["failover_count"] += 1
                eligible_providers.remove(provider)
                if not eligible_providers:
                    self.metrics["request_failed"] += 1
                    raise ProviderTimeoutError(provider=provider.provider_info.id, message=str(e)) from e
            except ConnectionError as e:
                provider.failure_flag = True
                self.metrics["failover_count"] += 1
                eligible_providers.remove(provider)
                if not eligible_providers:
                    self.metrics["request_failed"] += 1
                    raise ProviderUnavailableError(provider=provider.provider_info.id, message=str(e)) from e
            except (ValueError, PermissionError) as e:
                # 4. Authentication/Credential error -> exclude provider, do NOT trigger CB, failover
                self.metrics["failover_count"] += 1
                eligible_providers.remove(provider)
                if not eligible_providers:
                    self.metrics["request_failed"] += 1
                    raise ProviderAuthFailedError(provider=provider.provider_info.id, message=str(e)) from e
            except Exception as e:
                # 5. Handle HTTP status errors or other unexpected exceptions
                import httpx
                if isinstance(e, httpx.HTTPStatusError) and e.response.status_code in (401, 403):
                    self.metrics["failover_count"] += 1
                    eligible_providers.remove(provider)
                    if not eligible_providers:
                        self.metrics["request_failed"] += 1
                        raise ProviderAuthFailedError(provider=provider.provider_info.id, message=f"HTTP {e.response.status_code}") from e
                else:
                    # Treat other unexpected exceptions as connection failures (trigger CB)
                    provider.failure_flag = True
                    self.metrics["failover_count"] += 1
                    eligible_providers.remove(provider)
                    if not eligible_providers:
                        self.metrics["request_failed"] += 1
                        raise ProviderRequestFailedError(provider=provider.provider_info.id, message=str(e)) from e
