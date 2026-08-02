import pytest
from datetime import datetime, timezone

from orchx_core.interfaces.optimization_contracts import (
    OptimizationProfile,
    ExecutionTelemetry,
    ModelPerformanceHistory
)
from orchx_runtime.optimization_engine import OptimizationManager


# 1. Telemetry Registries & Rolling Benchmarks Tests
def test_telemetry_history_aggregation():
    manager = OptimizationManager()
    
    t1 = ExecutionTelemetry(
        execution_id="run-1",
        workflow_id="wf-1",
        task_count=3,
        provider="openai",
        model="gpt-4o",
        worker="w1",
        execution_duration=1.2,
        queue_wait_time=0.1,
        review_score=90.0,
        security_score=98.0,
        token_usage=1000,
        estimated_cost=0.015,
        retry_count=0,
        success=True
    )
    
    t2 = ExecutionTelemetry(
        execution_id="run-2",
        workflow_id="wf-1",
        task_count=3,
        provider="openai",
        model="gpt-4o",
        worker="w1",
        execution_duration=0.8,
        queue_wait_time=0.1,
        review_score=95.0,
        security_score=100.0,
        token_usage=1000,
        estimated_cost=0.015,
        retry_count=0,
        success=True
    )

    manager.record_telemetry(t1)
    manager.record_telemetry(t2)

    # Fetch aggregated history
    history = manager.telemetry_registry.get_history("gpt-4o")
    assert history is not None
    assert history.execution_count == 2
    assert history.average_latency == 1.0  # (1.2 + 0.8) / 2
    assert history.average_review_score == 92.5  # (90.0 + 95.0) / 2
    assert history.average_success_rate == 1.0


# 2. Statistical Outcome Predictions Tests
def test_prediction_engine():
    manager = OptimizationManager()
    
    # 1. Prediction with empty history -> returns defaults
    pred_default = manager.prediction_engine.predict_outcome("openai", "gpt-4o", [])
    assert pred_default["estimated_duration"] == 0.5
    assert pred_default["estimated_success_probability"] == 0.99

    # 2. Prediction with aggregated history
    hist = ModelPerformanceHistory(
        provider="openai",
        model="gpt-4o",
        execution_count=5,
        average_latency=2.5,
        average_cost=0.05,
        average_review_score=95.0,
        average_security_score=98.0,
        average_success_rate=0.80
    )
    
    pred_stat = manager.prediction_engine.predict_outcome("openai", "gpt-4o", [hist])
    assert pred_stat["estimated_duration"] == 2.5
    assert pred_stat["estimated_cost"] == 0.05
    assert pred_stat["estimated_success_probability"] == 0.80


# 3. Pluggable Recommendations Sorters Tests
def test_recommendation_engine_profiles():
    manager = OptimizationManager()

    # Register two models to compare
    t_gpt4 = ExecutionTelemetry(
        execution_id="run-g4",
        workflow_id="wf-1",
        task_count=2,
        provider="openai",
        model="gpt-4o",
        worker="w1",
        execution_duration=1.5,
        queue_wait_time=0.1,
        review_score=98.0,
        security_score=100.0,
        token_usage=2000,
        estimated_cost=0.040, # expensive
        retry_count=0,
        success=True
    )
    t_gpt3 = ExecutionTelemetry(
        execution_id="run-g3",
        workflow_id="wf-1",
        task_count=2,
        provider="openai",
        model="gpt-3.5-turbo",
        worker="w1",
        execution_duration=0.5,
        queue_wait_time=0.1,
        review_score=80.0,
        security_score=95.0,
        token_usage=2000,
        estimated_cost=0.004, # cheap
        retry_count=0,
        success=True
    )

    manager.record_telemetry(t_gpt4)
    manager.record_telemetry(t_gpt3)

    # 1. Compile report under LOWEST_COST profile
    report_cost = manager.compile_report(OptimizationProfile.LOWEST_COST)
    assert len(report_cost.recommendations) == 1
    rec = report_cost.recommendations[0]
    assert rec.recommendation_type == "model_swap"
    assert "gpt-3.5-turbo" in rec.description
    assert rec.expected_cost_change < 0.0 # expects cost savings

    # 2. Compile report under QUALITY profile
    report_quality = manager.compile_report(OptimizationProfile.QUALITY)
    assert len(report_quality.recommendations) == 1
    rec_q = report_quality.recommendations[0]
    assert "gpt-4o" in rec_q.description
    assert rec_q.expected_quality_change > 0.0


# 4. ExecutionDNA & Subsystem Metrics Tests
def test_execution_dna_generation():
    manager = OptimizationManager()
    
    telemetry = ExecutionTelemetry(
        execution_id="run-dna",
        workflow_id="wf-1",
        task_count=1,
        provider="ollama",
        model="mistral-7b",
        worker="w1",
        execution_duration=0.2,
        queue_wait_time=0.0,
        review_score=90.0,
        security_score=90.0,
        token_usage=500,
        estimated_cost=0.0,
        retry_count=0,
        success=True
    )

    dna = manager.generate_dna(
        execution_id="exec-dna",
        execution_report_id="rep-dna-101",
        telemetry=telemetry,
        review_report_id="rev-rep-202"
    )

    assert dna.execution_id == "exec-dna"
    assert dna.execution_report_id == "rep-dna-101"
    assert dna.review_report_id == "rev-rep-202"
    assert dna.telemetry.model == "mistral-7b"
