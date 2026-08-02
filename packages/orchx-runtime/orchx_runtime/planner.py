from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple, Optional

from orchx_core.interfaces.spec import (
    ProductSpecification,
    CategorizedRequirements,
    Requirement,
    ClarificationQuestion,
)
from orchx_core.interfaces.workflow import WorkflowDefinition


class RequirementExtractor:
    """
    Parses user requests to generate ProductSpecifications and assigns confidence scores.
    Automatically generates ClarificationQuestions for low-confidence fields.
    """

    def __init__(self, confidence_threshold: float = 0.7) -> None:
        self.confidence_threshold = confidence_threshold

    def extract(self, user_request: str) -> Tuple[ProductSpecification, List[ClarificationQuestion]]:
        # Mock deterministic extractor based on input keywords
        req_lower = user_request.lower()
        
        project_name = "OrchX App"
        project_type = "web_saas"
        project_description = user_request
        
        confidence_scores = {
            "project_name": 0.5,  # Unspecified, default assigned
            "project_type": 0.9 if "saas" in req_lower or "api" in req_lower else 0.4,
            "technology_preferences": 0.8 if "python" in req_lower or "react" in req_lower else 0.3,
            "target_platforms": 0.8 if "web" in req_lower or "ios" in req_lower else 0.3,
            "deployment_preferences": 0.3, # Always low confidence unless specified
            "acceptance_criteria": 0.5
        }

        # Extracted categories requirements
        functional_reqs = []
        if "saas" in req_lower:
            functional_reqs.append(
                Requirement(
                    id="REQ-FUN-01",
                    description="User authentication and billing dashboard.",
                    priority="high"
                )
            )

        spec = ProductSpecification(
            project_name=project_name,
            project_type=project_type,
            project_description=project_description,
            version="1.0.0",
            author_source="user",
            requirements=CategorizedRequirements(functional=functional_reqs),
            goals=["Build scalable system"],
            target_platforms=["Web"] if "web" in req_lower else [],
            technology_preferences=["Python"] if "python" in req_lower else [],
            acceptance_criteria=["System runs successfully"] if "successfully" in req_lower else [],
            confidence_scores=confidence_scores
        )

        clarifications = []
        # Check low-confidence fields to generate clarifications instead of guessing
        if confidence_scores["project_name"] < self.confidence_threshold:
            clarifications.append(
                ClarificationQuestion(
                    id="q-name",
                    field="project_name",
                    question="What is the name of your project?",
                    reason="The name is required to initialize project configurations."
                )
            )
        if confidence_scores["target_platforms"] < self.confidence_threshold:
            clarifications.append(
                ClarificationQuestion(
                    id="q-platform",
                    field="target_platforms",
                    question="Which target platforms should be supported (Web, iOS, Android)?",
                    options=["Web", "iOS", "Android"],
                    reason="Platforms determine the required workflow compilation structures."
                )
            )
        if confidence_scores["deployment_preferences"] < self.confidence_threshold:
            clarifications.append(
                ClarificationQuestion(
                    id="q-deploy",
                    field="deployment_preferences",
                    question="Where should the application be deployed (AWS, Vercel, Heroku)?",
                    options=["AWS", "Vercel", "Heroku"],
                    reason="Deployment target specifies the deployment step tooling."
                )
            )

        return spec, clarifications


class PlannerRulesEngine:
    """
    Evaluates the ProductSpecification parameters against deterministic mapping rules 
    to resolve the correct Workflow template.
    """

    def select_workflow(self, spec: ProductSpecification) -> Optional[str]:
        # Deterministic rule evaluations
        ptype = spec.project_type.lower()
        if ptype == "web_saas":
            return "web-sass-builder"
        elif ptype == "api_service":
            return "backend-api-builder"
        elif ptype == "mobile_app":
            return "mobile-app-builder"
        return None


class SpecificationVersionManager:
    """
    Manages spec edits by appending immutable version increments.
    """

    @staticmethod
    def update_specification(
        spec: ProductSpecification,
        updates: Dict[str, Any],
        change_summary: str,
        author: str = "agent"
    ) -> ProductSpecification:
        # Determine next minor version increment
        try:
            parts = spec.version.split(".")
            minor = int(parts[1]) + 1
            next_version = f"{parts[0]}.{minor}.0"
        except Exception:
            next_version = "1.1.0"

        # Merge updates with existing values
        dump = spec.model_dump()
        for k, v in updates.items():
            if k in dump:
                dump[k] = v

        dump["version"] = next_version
        dump["parent_version"] = spec.version
        dump["created_at"] = datetime.now(timezone.utc)
        dump["author_source"] = author
        dump["change_summary"] = change_summary

        return ProductSpecification(**dump)
