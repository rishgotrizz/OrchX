import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from orchx_core.interfaces.optimization_contracts import (
    OptimizationProfile,
    ExecutionTelemetry,
    ModelPerformanceHistory,
    Recommendation,
    OptimizationReport,
    ExecutionDNA,
    SystemMetrics,
)


class TelemetryRegistry:
    """
    Registry hosting immutable telemetry records and compiling model performance histories.
    """

    def __init__(self) -> None:
        self._telemetries: List[ExecutionTelemetry] = []
        self._history: Dict[str, ModelPerformanceHistory] = {}

    def record_telemetry(self, telemetry: ExecutionTelemetry) -> None:
        self._telemetries.append(telemetry)
        
        # Recalculate performance history stats dynamically
        model_id = telemetry.model
        provider_id = telemetry.provider
        
        # Extract matching telemetries
        matches = [t for t in self._telemetries if t.model == model_id and t.provider == provider_id]
        count = len(matches)
        
        avg_latency = sum(t.execution_duration for t in matches) / count
        avg_cost = sum(t.estimated_cost for t in matches) / count
        avg_review = sum(t.review_score for t in matches) / count
        avg_security = sum(t.security_score for t in matches) / count
        success_rate = sum(1 for t in matches if t.success) / count

        self._history[model_id] = ModelPerformanceHistory(
            provider=provider_id,
            model=model_id,
            execution_count=count,
            average_latency=avg_latency,
            average_cost=avg_cost,
            average_review_score=avg_review,
            average_security_score=avg_security,
            average_success_rate=success_rate,
            last_updated=datetime.now(timezone.utc)
        )

    def list_history(self) -> List[ModelPerformanceHistory]:
        return list(self._history.values())

    def get_history(self, model_id: str) -> Optional[ModelPerformanceHistory]:
        return self._history.get(model_id)


class PredictionEngine:
    """
    Generates statistical estimates of task runs using benchmark history.
    """

    def predict_outcome(self, provider_id: str, model_id: str, history: List[ModelPerformanceHistory]) -> Dict[str, Any]:
        match = next((h for h in history if h.model == model_id and h.provider == provider_id), None)
        if match:
            return {
                "estimated_duration": match.average_latency,
                "estimated_cost": match.average_cost,
                "estimated_quality": match.average_review_score,
                "estimated_security": match.average_security_score,
                "estimated_success_probability": match.average_success_rate
            }
        
        # Default baseline estimates
        return {
            "estimated_duration": 0.5,
            "estimated_cost": 0.005,
            "estimated_quality": 85.0,
            "estimated_security": 95.0,
            "estimated_success_probability": 0.99
        }


class RecommendationEngine:
    """
    Formulates advisory optimization recommendation records.
    """

    def generate_recommendations(
        self,
        history: List[ModelPerformanceHistory],
        profile: OptimizationProfile
    ) -> List[Recommendation]:
        recommendations = []

        if not history:
            return recommendations

        # Locate gpt-4o vs gpt-3.5-turbo for cost/quality evaluations
        gpt4 = next((h for h in history if h.model == "gpt-4o"), None)
        gpt35 = next((h for h in history if h.model == "gpt-3.5-turbo"), None)

        if gpt4 and gpt35:
            if profile == OptimizationProfile.LOWEST_COST:
                # Suggest swapping to gpt-3.5-turbo if cost is priority
                cost_diff = gpt35.average_cost - gpt4.average_cost
                latency_diff = gpt35.average_latency - gpt4.average_latency
                quality_diff = gpt35.average_review_score - gpt4.average_review_score
                
                recommendations.append(
                    Recommendation(
                        id=f"rec-{uuid.uuid4()}",
                        recommendation_type="model_swap",
                        description="Recommend swapping gpt-4o for gpt-3.5-turbo to lower execution cost.",
                        confidence=0.85,
                        expected_quality_change=quality_diff,
                        expected_latency_change=latency_diff,
                        expected_cost_change=cost_diff,
                        expected_reliability_change=gpt35.average_success_rate - gpt4.average_success_rate
                    )
                )
            elif profile == OptimizationProfile.QUALITY:
                # Suggest upgrading to gpt-4o if gpt-3.5 is slower or lower quality
                quality_diff = gpt4.average_review_score - gpt35.average_review_score
                if quality_diff > 0:
                    recommendations.append(
                        Recommendation(
                            id=f"rec-{uuid.uuid4()}",
                            recommendation_type="model_swap",
                            description="Recommend upgrading to gpt-4o to improve code review scores.",
                            confidence=0.90,
                            expected_quality_change=quality_diff,
                            expected_latency_change=gpt4.average_latency - gpt35.average_latency,
                            expected_cost_change=gpt4.average_cost - gpt35.average_cost,
                            expected_reliability_change=gpt4.average_success_rate - gpt35.average_success_rate
                        )
                    )

        return recommendations


class OptimizationManager:
    """
    Subsystem coordinator managing system metrics, ExecutionDNA creation, 
    and OptimizationReport logs compiles.
    """

    def __init__(self) -> None:
        self.telemetry_registry = TelemetryRegistry()
        self.prediction_engine = PredictionEngine()
        self.recommendation_engine = RecommendationEngine()
        self.system_metrics = SystemMetrics()

    def record_telemetry(self, telemetry: ExecutionTelemetry) -> None:
        self.telemetry_registry.record_telemetry(telemetry)

    def compile_report(self, profile: OptimizationProfile) -> OptimizationReport:
        history = self.telemetry_registry.list_history()
        recs = self.recommendation_engine.generate_recommendations(history, profile)
        
        # Sum estimated cost changes
        est_cost_savings = sum(r.expected_cost_change for r in recs)
        
        return OptimizationReport(
            report_id=f"opt-rep-{uuid.uuid4()}",
            optimization_profile=profile,
            benchmark_summary={"models_evaluated": len(history)},
            execution_summary={"total_runs": len(self.telemetry_registry._telemetries)},
            recommendations=recs,
            estimated_improvements={"cost_change": est_cost_savings},
            confidence=0.85
        )

    def generate_dna(
        self,
        execution_id: str,
        execution_report_id: str,
        telemetry: ExecutionTelemetry,
        review_report_id: Optional[str] = None,
        security_report_id: Optional[str] = None
    ) -> ExecutionDNA:
        """Assembles immutable ExecutionDNA record for replay audits."""
        return ExecutionDNA(
            dna_id=f"dna-{uuid.uuid4()}",
            execution_id=execution_id,
            execution_report_id=execution_report_id,
            review_report_id=review_report_id,
            security_report_id=security_report_id,
            telemetry=telemetry
        )
