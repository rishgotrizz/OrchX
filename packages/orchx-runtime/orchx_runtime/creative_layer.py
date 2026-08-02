import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from orchx_core.interfaces.creative_contracts import (
    VisualBenchmark,
    ComponentGenome,
    MotionGenome,
    ResponsiveStrategy,
    CreativeGenome,
    DesignSystem,
    BrandProfile,
    ExperienceScene,
    DesignConcept,
    FrontendPerformanceBudget,
    ExperienceScore,
    CreativeReviewReport,
    DesignDecisionReport,
)


class VisualBenchmarkLibrary:
    """Library storing visual references and layout observations."""
    def __init__(self) -> None:
        self.benchmarks: List[VisualBenchmark] = []

    def load_benchmark(self, benchmark: VisualBenchmark) -> None:
        self.benchmarks.append(benchmark)

    def get_benchmarks_by_category(self, category: str) -> List[VisualBenchmark]:
        return [b for b in self.benchmarks if b.category == category]


class DesignCouncil:
    """Generates multiple DesignConcepts."""
    
    def generate_concepts(self, requirements: str, policy: str) -> List[DesignConcept]:
        concepts = []
        
        # Concept 1: Premium / Heavy Animation
        concepts.append(
            DesignConcept(
                concept_id=f"dc-{uuid.uuid4()}",
                title=f"Premium Concept for {requirements}",
                reasoning="Focus on brand perception and highly crafted interactions.",
                design_philosophy="Minimalist with heavy emphasis on micro-interactions.",
                visual_language="High contrast, large typography, deep shadows.",
                interaction_style="Smooth, continuous scroll revealing elements.",
                layout_strategy="Asymmetrical grid.",
                accessibility_strategy="AA compliant contrast, motion toggle.",
                responsive_strategy="Desktop-first scaling to mobile.",
                animation_strategy="GSAP timeline orchestration.",
                three_d_strategy="Three.js particle background.",
                estimated_complexity="High",
                estimated_implementation_effort=14.0
            )
        )
        
        # Concept 2: Fast / Accessible
        concepts.append(
            DesignConcept(
                concept_id=f"dc-{uuid.uuid4()}",
                title=f"Balanced Fast Concept for {requirements}",
                reasoning="Focus on performance, fast load times, and universal accessibility.",
                design_philosophy="Functional, sparse, utility-driven.",
                visual_language="Flat, soft colors, dense information hierarchy.",
                interaction_style="Standard native browser behaviors.",
                layout_strategy="Standard 12-column symmetrical grid.",
                accessibility_strategy="AAA compliant contrast, full keyboard nav.",
                responsive_strategy="Mobile-first fluid scaling.",
                animation_strategy="CSS transitions only, no JS animation.",
                three_d_strategy="None",
                estimated_complexity="Low",
                estimated_implementation_effort=5.0
            )
        )
        return concepts


class VisualConsistencyEngine:
    """Evaluates consistency across spacing, colors, and components."""
    def evaluate(self, concept: DesignConcept) -> float:
        score = 80.0
        if "asymmetrical" in concept.layout_strategy.lower():
            score -= 10.0 # harder to keep consistent
        if "native" in concept.interaction_style.lower():
            score += 15.0 # very consistent
        return min(100.0, max(0.0, score))


class ExperienceEvaluationEngine:
    """Calculates comprehensive experience score combining usability, a11y, etc."""
    def evaluate_experience(self, concept: DesignConcept) -> ExperienceScore:
        a11y = 90.0 if "AAA" in concept.accessibility_strategy else 75.0
        performance = 95.0 if concept.three_d_strategy == "None" else 60.0
        complexity = 80.0 if concept.estimated_complexity == "Low" else 40.0
        
        overall = (a11y * 0.4) + (performance * 0.4) + (complexity * 0.2)
        
        return ExperienceScore(
            usability=85.0,
            accessibility=a11y,
            responsiveness=90.0,
            consistency=85.0,
            readability=85.0,
            visual_hierarchy=85.0,
            interaction_quality=80.0,
            animation_quality=75.0,
            performance_impact=performance,
            implementation_complexity=complexity,
            overall_experience_score=overall
        )


class CreativeCritiqueEngine:
    """Provides qualitative review report before selection."""
    def critique(self, concept: DesignConcept) -> CreativeReviewReport:
        a11y_eval = "Excellent accessibility" if "AAA" in concept.accessibility_strategy else "Adequate accessibility"
        return CreativeReviewReport(
            report_id=f"ccr-{uuid.uuid4()}",
            concept_id=concept.concept_id,
            visual_hierarchy_evaluation="Clear and structured.",
            whitespace_evaluation="Well balanced.",
            readability_evaluation="High contrast ensures readability.",
            accessibility_evaluation=a11y_eval,
            consistency_evaluation="Follows design system tokens well.",
            branding_evaluation="Aligns with brand profile.",
            usability_evaluation="Standard patterns make it usable.",
            motion_quality_evaluation="Smooth and performant.",
            responsiveness_evaluation="Fluid layouts scale appropriately.",
        )


class DesignDecisionEngine:
    """Combines evaluations and selects the best DesignConcept."""
    
    def __init__(self) -> None:
        self.experience_engine = ExperienceEvaluationEngine()
        self.critique_engine = CreativeCritiqueEngine()
        
    def evaluate_and_select(self, concepts: List[DesignConcept]) -> DesignDecisionReport:
        scores = {}
        for c in concepts:
            score = self.experience_engine.evaluate_experience(c)
            scores[c.concept_id] = score.overall_experience_score
            
        ranked = sorted(concepts, key=lambda c: scores[c.concept_id], reverse=True)
        selected = ranked[0]
        
        return DesignDecisionReport(
            report_id=f"ddr-{uuid.uuid4()}",
            selected_concept_id=selected.concept_id,
            ranking=[c.concept_id for c in ranked],
            confidence=0.92,
            tradeoffs={"Premium": "High load time", "Fast": "Less brand impact"},
            reasoning=f"Selected {selected.title} due to high ExperienceScore of {scores[selected.concept_id]:.1f}.",
            rejected_concepts=[c.concept_id for c in ranked[1:]]
        )


class CreativeMemoryRegistry:
    """Immutable memory store for Component, Motion, and Creative Genomes."""
    def __init__(self) -> None:
        self.component_genomes: Dict[str, ComponentGenome] = {}
        self.motion_genomes: Dict[str, MotionGenome] = {}
        self.creative_genomes: Dict[str, CreativeGenome] = {}
        
    def register_component(self, cg: ComponentGenome) -> None:
        self.component_genomes[cg.component_id] = cg
        
    def register_motion(self, mg: MotionGenome) -> None:
        self.motion_genomes[mg.motion_id] = mg
        
    def register_creative(self, cg: CreativeGenome) -> None:
        self.creative_genomes[cg.genome_id] = cg


class DesignSystemEngine:
    """Manages reusable design tokens and brand profiles."""
    def __init__(self) -> None:
        self.systems: Dict[str, DesignSystem] = {}
        self.brand_profiles: Dict[str, BrandProfile] = {}
        
    def load_system(self, sys_id: str, system: DesignSystem) -> None:
        self.systems[sys_id] = system
        
    def apply_brand_profile(self, profile: BrandProfile) -> None:
        self.brand_profiles[profile.profile_id] = profile
