from typing import Dict, Any, List
from datetime import datetime, timezone
from orchx_core.interfaces.provider_contracts import Model, UsageMetrics

class CostCalculator:
    """
    Calculates cost for a request based on usage metrics and pricing tables.
    """
    @classmethod
    def calculate(cls, model: Model, usage: UsageMetrics) -> float:
        """
        Calculate total cost of a request based on model pricing.
        Cost is derived from prompt and completion token counts.
        """
        prompt_cost = (usage.prompt_tokens * model.cost_per_million_prompt) / 1000000.0
        completion_cost = (usage.completion_tokens * model.cost_per_million_completion) / 1000000.0
        return prompt_cost + completion_cost

class BillingEngine:
    """
    Central accounting engine for Provider token consumption.
    Independent from networking layer.
    """
    def __init__(self):
        self.usage_history: List[Dict[str, Any]] = []

    def record_usage(self, provider_id: str, model: Model, usage: UsageMetrics) -> None:
        """
        Calculate cost and record the usage transaction.
        Updates the UsageMetrics object with the estimated cost in-place.
        """
        cost = CostCalculator.calculate(model, usage)
        usage.estimated_cost = cost
        
        transaction = {
            "provider_id": provider_id,
            "model_id": model.id,
            "prompt_tokens": usage.prompt_tokens,
            "completion_tokens": usage.completion_tokens,
            "cached_tokens": usage.cached_tokens,
            "total_tokens": usage.total_tokens,
            "latency_ms": usage.latency_ms,
            "estimated_cost": cost,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self.usage_history.append(transaction)
