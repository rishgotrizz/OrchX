import pytest
from typing import Dict, Any

from orchx_core.interfaces.spec import (
    ProductSpecification,
    CategorizedRequirements,
    Requirement,
    ClarificationQuestion,
)
from orchx_runtime.planner import (
    RequirementExtractor,
    PlannerRulesEngine,
    SpecificationVersionManager,
)
from orchx_runtime.spec_validator import ProductSpecificationValidator


# 1. Requirement Parsing & Clarification Tests
def test_requirement_extractor_and_confidence():
    extractor = RequirementExtractor(confidence_threshold=0.7)
    
    # Query specifying SaaS but leaving out platforms and deployment details
    spec, clarifications = extractor.extract("Build me a python SaaS successfully")
    
    assert spec.project_type == "web_saas"
    assert spec.confidence_scores["project_type"] == 0.9  # High confidence
    assert spec.confidence_scores["deployment_preferences"] == 0.3  # Low confidence
    
    # Low confidence triggers clarification questions
    assert len(clarifications) > 0
    q_fields = [q.field for q in clarifications]
    assert "deployment_preferences" in q_fields
    assert "target_platforms" in q_fields


# 2. Specification Validation Tests
def test_spec_validation_success():
    spec = ProductSpecification(
        project_name="OrchX App",
        project_type="web_saas",
        project_description="Build a high-performance system successfully",
        acceptance_criteria=["Criterion 1"]
    )
    
    errors = ProductSpecificationValidator.validate(spec)
    assert len(errors) == 0


def test_spec_validation_missing_fields_and_criteria():
    spec = ProductSpecification(
        project_name="",
        project_type="web_saas",
        project_description="Short",
        acceptance_criteria=[]
    )
    
    errors = ProductSpecificationValidator.validate(spec)
    assert len(errors) == 3
    err_types = {e["error_type"] for e in errors}
    assert "MISSING_FIELD" in err_types
    assert "INVALID_FIELD" in err_types
    assert "MISSING_ACCEPTANCE_CRITERIA" in err_types


def test_spec_validation_conflicting_constraints():
    spec = ProductSpecification(
        project_name="iOS Swift Tool",
        project_type="api_service",
        project_description="Swift API development workspace",
        technology_preferences=["Swift"],
        target_platforms=["Android"],  # Swift on Android targets conflict
        acceptance_criteria=["Built successfully"]
    )
    
    errors = ProductSpecificationValidator.validate(spec)
    assert len(errors) == 1
    assert errors[0]["error_type"] == "CONFLICTING_CONSTRAINTS"


def test_spec_validation_circular_requirements():
    req_a = Requirement(
        id="REQ-FUN-01",
        description="F1",
        metadata={"dependencies": ["REQ-FUN-02"]}
    )
    req_b = Requirement(
        id="REQ-FUN-02",
        description="F2",
        metadata={"dependencies": ["REQ-FUN-01"]}
    )

    spec = ProductSpecification(
        project_name="Circ App",
        project_type="web_saas",
        project_description="App with circular functional requirements",
        requirements=CategorizedRequirements(functional=[req_a, req_b]),
        acceptance_criteria=["Built successfully"]
    )

    errors = ProductSpecificationValidator.validate(spec)
    assert len(errors) == 1
    assert errors[0]["error_type"] == "CIRCULAR_DEPENDENCY"


# 3. Workflow Selection Rules Tests
def test_planner_rules_workflow_selection():
    engine = PlannerRulesEngine()
    
    spec_saas = ProductSpecification(
        project_name="App",
        project_type="web_saas",
        project_description="Descr",
        acceptance_criteria=["1"]
    )
    assert engine.select_workflow(spec_saas) == "web-sass-builder"

    spec_api = ProductSpecification(
        project_name="App",
        project_type="api_service",
        project_description="Descr",
        acceptance_criteria=["1"]
    )
    assert engine.select_workflow(spec_api) == "backend-api-builder"


# 4. Immutable Versioning Tests
def test_specification_versioning_manager():
    spec_v1 = ProductSpecification(
        project_name="App v1",
        project_type="web_saas",
        project_description="Initial description",
        version="1.0.0",
        acceptance_criteria=["1"]
    )

    spec_v2 = SpecificationVersionManager.update_specification(
        spec_v1,
        {"project_name": "App v2"},
        change_summary="Upgraded project name to v2",
        author="agent"
    )

    # Immutability check
    assert spec_v1.project_name == "App v1"
    assert spec_v1.version == "1.0.0"

    # Version tracking verification
    assert spec_v2.project_name == "App v2"
    assert spec_v2.version == "1.1.0"
    assert spec_v2.parent_version == "1.0.0"
    assert spec_v2.change_summary == "Upgraded project name to v2"
    assert spec_v2.author_source == "agent"
