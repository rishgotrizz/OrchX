from typing import Any, Dict, List, Optional, Tuple
from orchx_core.interfaces.provider_contracts import (
    BaseProvider,
    Model,
    ProviderRequest,
    ProviderSelectionStrategy,
)


class DefaultSelectionStrategy(ProviderSelectionStrategy):
    """
    Selects the first registered model that satisfies all requested capabilities.
    """

    def select_model(
        self,
        required_capabilities: List[str],
        providers: List[BaseProvider]
    ) -> Optional[Tuple[BaseProvider, Model]]:
        for provider in providers:
            # Skip failed providers
            if provider.failure_flag:
                continue
            for model in provider.list_models():
                if model.status != "online":
                    continue
                # Match all required capabilities
                if all(cap in model.capabilities for cap in required_capabilities):
                    return provider, model
        return None


class LowestLatencyStrategy(ProviderSelectionStrategy):
    """
    Selects the compatible model whose parent provider reports the lowest request latency.
    """

    def select_model(
        self,
        required_capabilities: List[str],
        providers: List[BaseProvider]
    ) -> Optional[Tuple[BaseProvider, Model]]:
        candidates = []
        for provider in providers:
            if provider.failure_flag:
                continue
            for model in provider.list_models():
                if model.status != "online":
                    continue
                if all(cap in model.capabilities for cap in required_capabilities):
                    candidates.append((provider, model))
        
        if not candidates:
            return None

        # Sort candidates by provider latency
        return sorted(candidates, key=lambda c: c[0].latency)[0]


class OptimizedSelectionStrategy(ProviderSelectionStrategy):
    """
    Selects the most suitable model using the Decision and Optimization engines,
    weighing capabilities, trust, latency, cost, quality, and optimization profile.
    """

    def __init__(self, profile: "OptimizationProfile", opt_manager: "OptimizationManager"):
        self.profile = profile
        self.opt_manager = opt_manager

    def select_model(
        self,
        required_capabilities: List[str],
        providers: List[BaseProvider]
    ) -> Optional[Tuple[BaseProvider, Model]]:
        from orchx_core.interfaces.optimization_contracts import OptimizationProfile

        candidates = []
        for provider in providers:
            if getattr(provider, "failure_flag", False):
                continue
            for model in provider.list_models():
                if model.status != "online":
                    continue
                if all(cap in model.capabilities for cap in required_capabilities):
                    candidates.append((provider, model))
        
        if not candidates:
            return None

        history = self.opt_manager.telemetry_registry.list_history()
        scored_candidates = []

        for provider, model in candidates:
            pred = self.opt_manager.prediction_engine.predict_outcome(
                provider.provider_info.id, model.id, history
            )
            
            # Extract metrics
            latency = pred["estimated_duration"]
            cost = pred["estimated_cost"]
            quality = pred["estimated_quality"]
            security = pred["estimated_security"]
            reliability = pred["estimated_success_probability"]

            # Higher is better for all metrics in scoring
            # Normalize latency and cost (lower is better, so invert)
            inv_latency = max(0, 10.0 - latency) / 10.0 * 100.0 if latency < 10.0 else 0
            inv_cost = max(0, 0.1 - cost) / 0.1 * 100.0 if cost < 0.1 else 0

            if self.profile == OptimizationProfile.LOWEST_COST:
                score = (inv_cost * 0.6) + (quality * 0.2) + (inv_latency * 0.2)
            elif self.profile == OptimizationProfile.SPEED:
                score = (inv_latency * 0.5) + (reliability * 0.3) + (inv_cost * 0.2)
            elif self.profile == OptimizationProfile.QUALITY:
                score = (quality * 0.4) + (reliability * 0.4) + (security * 0.2)
            else:
                score = (quality * 0.25) + (reliability * 0.25) + (inv_cost * 0.25) + (inv_latency * 0.25)
            
            scored_candidates.append((score, provider, model))

        # Sort by score descending
        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        return scored_candidates[0][1], scored_candidates[0][2]
