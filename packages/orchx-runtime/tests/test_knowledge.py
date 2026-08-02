import pytest
from datetime import datetime, timezone

from orchx_core.interfaces.knowledge_contracts import EngineeringMemoryEntry
from orchx_runtime.knowledge_layer import (
    EngineeringMemoryRegistry,
    AntiPatternRegistry,
    PrinciplesEngine,
    EngineeringRecommendationEngine,
)


# 1. EngineeringMemory Storage & Rolling Confidence Tests
def test_engineering_memory_registry_confidence_decay():
    registry = EngineeringMemoryRegistry()
    
    entry = EngineeringMemoryEntry(
        entry_id="mem-k-01",
        entry_type="architecture",
        content={"design": "Monolithic backend API"},
        confidence=0.5
    )
    registry.store(entry)

    # 1. Successful run validation increases confidence
    registry.record_validation("mem-k-01", success=True)
    updated = registry.get("mem-k-01")
    assert updated.confidence == pytest.approx(0.55)
    assert updated.evidence_count == 1
    assert updated.successful_projects == 1

    # 2. Failed run validation decays confidence
    registry.record_validation("mem-k-01", success=False)
    updated_fail = registry.get("mem-k-01")
    # 0.55 - 0.10 = 0.45
    assert updated_fail.confidence == pytest.approx(0.45)
    assert updated_fail.failed_projects == 1


# 2. Anti-Pattern Detection Scans Tests
def test_antipattern_registry_scanners():
    registry = AntiPatternRegistry()

    # 1. God Object scan (very long file > 200 lines)
    long_content = "def test():\n    pass\n" * 105
    violations_god = registry.detect_violations(long_content, "main.py")
    assert len(violations_god) == 1
    assert violations_god[0].id == "god_object"

    # 2. Circular dependency scan (filename contains circular and import in content)
    viol_circ = registry.detect_violations("import routes\nimport core", "circular_imports.py")
    assert len(viol_circ) == 1
    assert viol_circ[0].id == "circular_dependency"

    # 3. SQL in Controllers scan
    viol_sql = registry.detect_violations("db.execute('SELECT * FROM users')", "user_routes.py")
    assert len(viol_sql) == 1
    assert viol_sql[0].id == "inline_sql"

    # 4. Clean file should trigger zero violations
    viol_ok = registry.detect_violations("def test():\n    pass", "routes.py")
    assert len(viol_ok) == 0


# 3. Principles Evaluation & Recommendation Generation Tests
def test_principles_and_recommendations_matching():
    principles_engine = PrinciplesEngine()
    recs_engine = EngineeringRecommendationEngine()

    # 1. Evaluate compliance score adjustments
    compliance = principles_engine.evaluate_compliance(["stripe", "plugin_system"])
    assert compliance == 95.0 # baseline 80 + 15 (modular plugin keyword matched)

    # 2. Generate recommendations (billings stack suggests payments genome)
    recs = recs_engine.generate_recommendations(["stripe", "python"], [])
    assert len(recs) == 1
    assert recs[0].recommendation_type == "reuse_genome"
    assert "payments" in recs[0].description
    assert recs[0].governing_principle_id == "plugin_first"
