from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CreativeRole(str, Enum):
    CREATIVE_DIRECTOR = "creative_director"
    UX_RESEARCHER = "ux_researcher"
    UX_DESIGNER = "ux_designer"
    UI_DESIGNER = "ui_designer"
    BRAND_DESIGNER = "brand_designer"
    MOTION_DESIGNER = "motion_designer"
    THREE_D_DESIGNER = "3d_designer"
    FRONTEND_ARCHITECT = "frontend_architect"
    ACCESSIBILITY_REVIEWER = "accessibility_reviewer"
    DESIGN_SYSTEM_ARCHITECT = "design_system_architect"


class VisualBenchmark(BaseModel):
    benchmark_id: str
    category: str
    layout_principles: List[str] = Field(default_factory=list)
    interaction_philosophy: str
    accessibility_observations: List[str] = Field(default_factory=list)
    motion_philosophy: str
    responsive_strategy: str
    usability_observations: List[str] = Field(default_factory=list)
    engineering_considerations: List[str] = Field(default_factory=list)


class ComponentGenome(BaseModel):
    component_id: str
    purpose: str
    variants: List[str] = Field(default_factory=list)
    accessibility_requirements: List[str] = Field(default_factory=list)
    responsive_behavior: str
    animation_behavior: str
    design_tokens: Dict[str, Any] = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)
    engineering_guidance: str
    testing_guidance: str


class MotionGenome(BaseModel):
    motion_id: str
    timing: float
    easing: str
    accessibility_behavior: str
    reduced_motion_fallback: str
    performance_budget: str
    implementation_guidance: str


class ResponsiveStrategy(BaseModel):
    strategy_id: str
    layout_adaptation: str
    typography_scaling: str
    spacing_adaptation: str
    navigation_adaptation: str
    interaction_adaptation: str


class CreativeGenome(BaseModel):
    genome_id: str
    layout_blueprint: str
    ui_components: List[str] = Field(default_factory=list)
    ux_flows: List[str] = Field(default_factory=list)
    animation_guidelines: List[str] = Field(default_factory=list)
    responsive_behavior: str
    accessibility_requirements: List[str] = Field(default_factory=list)
    three_d_integration_rules: List[str] = Field(default_factory=list)


class DesignSystem(BaseModel):
    version: str
    semantic_colors: Dict[str, str] = Field(default_factory=dict)
    typography_scales: Dict[str, str] = Field(default_factory=dict)
    spacing_scales: Dict[str, str] = Field(default_factory=dict)
    elevation: Dict[str, str] = Field(default_factory=dict)
    shadows: Dict[str, str] = Field(default_factory=dict)
    border_radius: Dict[str, str] = Field(default_factory=dict)
    breakpoints: Dict[str, str] = Field(default_factory=dict)
    motion_durations: Dict[str, str] = Field(default_factory=dict)
    easing_curves: Dict[str, str] = Field(default_factory=dict)
    z_index_layers: Dict[str, str] = Field(default_factory=dict)
    accessibility_tokens: Dict[str, Any] = Field(default_factory=dict)


class BrandProfile(BaseModel):
    profile_id: str
    personality: str
    tone: str
    color_palette: Dict[str, str] = Field(default_factory=dict)
    typography: Dict[str, str] = Field(default_factory=dict)
    spacing_philosophy: str
    illustration_style: str
    iconography: str
    motion_identity: str


class ExperienceScene(BaseModel):
    """Structured scene specification (Three.js/WebGL/etc). No direct generation."""
    scene_id: str
    engine: str
    camera_settings: Dict[str, Any] = Field(default_factory=dict)
    lighting_settings: List[Dict[str, Any]] = Field(default_factory=list)
    physics_integrations: List[str] = Field(default_factory=list)
    scroll_interactions: List[str] = Field(default_factory=list)
    particle_systems: List[str] = Field(default_factory=list)


class DesignConcept(BaseModel):
    concept_id: str
    title: str
    reasoning: str
    design_philosophy: str
    visual_language: str
    interaction_style: str
    layout_strategy: str
    accessibility_strategy: str
    responsive_strategy: str
    animation_strategy: str
    three_d_strategy: str
    estimated_complexity: str
    estimated_implementation_effort: float


class FrontendPerformanceBudget(BaseModel):
    js_bundle_size_kb: float = 0.0
    css_size_kb: float = 0.0
    image_weight_kb: float = 0.0
    animation_cost_ms: float = 0.0
    webgl_complexity: str = "none"
    rendering_complexity: str = "low"
    hydration_cost_ms: float = 0.0


class ExperienceScore(BaseModel):
    usability: float = 0.0
    accessibility: float = 0.0
    responsiveness: float = 0.0
    consistency: float = 0.0
    readability: float = 0.0
    visual_hierarchy: float = 0.0
    interaction_quality: float = 0.0
    animation_quality: float = 0.0
    performance_impact: float = 0.0
    implementation_complexity: float = 0.0
    overall_experience_score: float = 0.0


class CreativeReviewReport(BaseModel):
    report_id: str
    concept_id: str
    visual_hierarchy_evaluation: str
    whitespace_evaluation: str
    readability_evaluation: str
    accessibility_evaluation: str
    consistency_evaluation: str
    branding_evaluation: str
    usability_evaluation: str
    motion_quality_evaluation: str
    responsiveness_evaluation: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DesignDecisionReport(BaseModel):
    report_id: str
    selected_concept_id: str
    ranking: List[str] = Field(default_factory=list)
    confidence: float
    tradeoffs: Dict[str, str] = Field(default_factory=dict)
    reasoning: str
    rejected_concepts: List[str] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
