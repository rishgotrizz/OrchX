from typing import Any, Dict, List, Optional, Tuple

from orchx_core.interfaces.provider_contracts import (
    BaseProvider,
    Model,
    ProviderRequest,
    ProviderResponse,
    ProviderSelectionStrategy,
)
from orchx_runtime.selection_strategies import DefaultSelectionStrategy


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
        Resolve compatible model, normalizes request, executes with retries, 
        and switches to alternative adapters on connection failures.
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
                raise ValueError("Outage resolution failed: No online provider models satisfy capabilities.")

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
            except (ConnectionError, TimeoutError) as e:
                # 3. Intercept outage, mark offline, trigger failover
                provider.failure_flag = True
                self.metrics["failover_count"] += 1
                
                # Exclude failed provider from next iteration
                eligible_providers.remove(provider)
                
                # If there are no more eligible adapters, raise error
                if not eligible_providers:
                    self.metrics["request_failed"] += 1
                    raise ConnectionError(f"All compatible providers failed: {e}") from e
