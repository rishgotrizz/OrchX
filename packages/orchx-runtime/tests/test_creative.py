import pytest
from orchx_core.interfaces.creative_contracts import (
    ComponentGenome,
    DesignSystem,
    BrandProfile
)
from orchx_runtime.creative_layer import (
    DesignCouncil,
    ExperienceEvaluationEngine,
    CreativeCritiqueEngine,
    DesignDecisionEngine,
    CreativeMemoryRegistry,
    DesignSystemEngine
)

def test_design_council_generates_concepts():
    council = DesignCouncil()
    concepts = council.generate_concepts("Build SaaS Dashboard", "Balanced")
    assert len(concepts) == 2
    assert "Premium" in concepts[0].title
    assert "Fast" in concepts[1].title


def test_experience_evaluation_engine():
    council = DesignCouncil()
    concepts = council.generate_concepts("Requirements", "Balanced")
    engine = ExperienceEvaluationEngine()
    
    score_premium = engine.evaluate_experience(concepts[0])
    score_fast = engine.evaluate_experience(concepts[1])
    
    # Fast concept should have better a11y & performance scores
    assert score_fast.accessibility > score_premium.accessibility
    assert score_fast.performance_impact > score_premium.performance_impact
    assert score_fast.overall_experience_score > score_premium.overall_experience_score


def test_creative_critique_engine():
    council = DesignCouncil()
    concepts = council.generate_concepts("Requirements", "Balanced")
    engine = CreativeCritiqueEngine()
    
    critique = engine.critique(concepts[1])
    assert "Excellent accessibility" in critique.accessibility_evaluation


def test_design_decision_engine():
    council = DesignCouncil()
    concepts = council.generate_concepts("Requirements", "Balanced")
    engine = DesignDecisionEngine()
    
    report = engine.evaluate_and_select(concepts)
    
    # Fast concept should win due to higher experience score
    assert "Fast Concept" in report.reasoning
    assert report.selected_concept_id == concepts[1].concept_id
    assert len(report.rejected_concepts) == 1
    assert report.rejected_concepts[0] == concepts[0].concept_id


def test_creative_memory_registry():
    registry = CreativeMemoryRegistry()
    cg = ComponentGenome(
        component_id="cg-button",
        purpose="Trigger actions",
        responsive_behavior="Full width on mobile",
        animation_behavior="Hover lift",
        engineering_guidance="Use native button tag",
        testing_guidance="Check keyboard focus"
    )
    registry.register_component(cg)
    assert "cg-button" in registry.component_genomes


def test_design_system_engine():
    engine = DesignSystemEngine()
    ds = DesignSystem(
        version="1.0.0",
        semantic_colors={"primary": "#0055FF"},
        breakpoints={"mobile": "320px"}
    )
    engine.load_system("ds-core", ds)
    assert engine.systems["ds-core"].semantic_colors["primary"] == "#0055FF"
    
    bp = BrandProfile(
        profile_id="bp-acme",
        personality="Playful",
        tone="Casual",
        spacing_philosophy="Airy",
        illustration_style="Flat vectors",
        iconography="Line icons",
        motion_identity="Bouncy"
    )
    engine.apply_brand_profile(bp)
    assert engine.brand_profiles["bp-acme"].personality == "Playful"
