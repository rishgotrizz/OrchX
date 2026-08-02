import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from orchx_core.interfaces.knowledge_contracts import (
    EngineeringMemoryEntry,
    ArchitectureGenome,
    EngineeringPrinciple,
    Pattern,
    AntiPattern,
    EngineeringRecommendation,
    EngineeringKnowledgeReport,
)


class EngineeringMemoryRegistry:
    """
    Registry managing permanent, immutable engineering knowledge entries.
    Confidence ratings increase/decrease through repeated success/failure runs.
    """

    def __init__(self) -> None:
        self._entries: Dict[str, EngineeringMemoryEntry] = {}

    def store(self, entry: EngineeringMemoryEntry) -> None:
        self._entries[entry.entry_id] = entry

    def get(self, entry_id: str) -> Optional[EngineeringMemoryEntry]:
        return self._entries.get(entry_id)

    def list_all(self) -> List[EngineeringMemoryEntry]:
        return list(self._entries.values())

    def record_validation(self, entry_id: str, success: bool) -> None:
        """Dynamically adjusts confidence parameters based on run results."""
        entry = self._entries.get(entry_id)
        if not entry:
            return

        ev_count = entry.evidence_count + 1
        success_projects = entry.successful_projects
        failed_projects = entry.failed_projects

        if success:
            success_projects += 1
            # Rolling confidence increase up to 1.0
            new_conf = min(1.0, entry.confidence + 0.05)
        else:
            failed_projects += 1
            # Confidence decay on failures
            new_conf = max(0.0, entry.confidence - 0.10)

        updated = EngineeringMemoryEntry(
            entry_id=entry_id,
            entry_type=entry.entry_type,
            content=entry.content,
            confidence=new_conf,
            evidence_count=ev_count,
            successful_projects=success_projects,
            failed_projects=failed_projects,
            last_validated=datetime.now(timezone.utc),
            timestamp=entry.timestamp
        )
        self._entries[entry_id] = updated


class AntiPatternRegistry:
    """
    Scanners looking for tight couplings or god objects in files.
    """

    def __init__(self) -> None:
        self._antipatterns = [
            AntiPattern(
                id="god_object",
                name="God Object",
                description="Class contains excessive responsibilities or lines of code.",
                remedy="Decompose class into modular services conforming to single responsibility rules."
            ),
            AntiPattern(
                id="circular_dependency",
                name="Circular Dependency",
                description="Two modules import each other directly.",
                remedy="Decouple imports boundary using shared interfaces or event buses."
            ),
            AntiPattern(
                id="inline_sql",
                name="Inline SQL in Controllers",
                description="SQL queries are written inside controller endpoint routes.",
                remedy="Move queries to data repository layer."
            )
        ]

    def detect_violations(self, content: str, file_name: str) -> List[AntiPattern]:
        violations = []
        
        # 1. God object check (mock line count check)
        if len(content.splitlines()) > 200:
            god = next(ap for ap in self._antipatterns if ap.id == "god_object")
            violations.append(god)

        # 2. Circular dependency imports mock check
        if "import" in content and "circular" in file_name.lower():
            circ = next(ap for ap in self._antipatterns if ap.id == "circular_dependency")
            violations.append(circ)

        # 3. SQL in Controllers check
        is_controller = "route" in file_name.lower() or "controller" in file_name.lower()
        if is_controller and ("select " in content.lower() or "insert " in content.lower()):
            sql = next(ap for ap in self._antipatterns if ap.id == "inline_sql")
            violations.append(sql)

        return violations


class PrinciplesEngine:
    """
    Evaluates candidates against design principles (Least Privilege, Plugin First).
    """

    def __init__(self) -> None:
        self.principles = [
            EngineeringPrinciple(id="plugin_first", name="Plugin First", description="Decoupled plugins"),
            EngineeringPrinciple(id="least_privilege", name="Least Privilege", description="Minimal capabilities restrictions")
        ]

    def evaluate_compliance(self, candidate_techs: List[str]) -> float:
        # Simplistic mock calculation: if codebase leverages modular plugins, compliance is higher
        score = 80.0
        if any("plugin" in t.lower() for t in candidate_techs):
            score += 15.0
        return min(100.0, score)


class EngineeringRecommendationEngine:
    """
    Provides advisory suggestions to reuse genomes or fix anti-patterns.
    """

    def __init__(self) -> None:
        self.genomes = [
            ArchitectureGenome(
                genome_id="auth",
                purpose="User signups and sessions verification",
                responsibilities=["Encrypt credentials", "Manage JWT tokens"],
                required_capabilities=["database.write"],
                dependencies=[],
                implementation_patterns=["OAuth2"],
                security_patterns=["Hashing"],
                testing_patterns=["Mock tokens"],
                deployment_considerations="Configure JWT secret vault key."
            ),
            ArchitectureGenome(
                genome_id="payments",
                purpose="Stripe integrations gateway",
                responsibilities=["Checkout redirects", "Process refunds"],
                required_capabilities=["network.outbound"],
                dependencies=["auth"],
                implementation_patterns=["Adapter"],
                security_patterns=["TLS"],
                testing_patterns=["Stripe mock"],
                deployment_considerations="Configure Stripe API vault key."
            )
        ]

    def generate_recommendations(
        self,
        candidate_techs: List[str],
        violated_antipatterns: List[AntiPattern]
    ) -> List[EngineeringRecommendation]:
        recs = []

        # 1. Check if candidate stack has payments tags but lacks payments genome integration
        has_payments_tech = any(x in [t.lower() for t in candidate_techs] for x in ["stripe", "paypal", "billing"])
        if has_payments_tech:
            recs.append(
                EngineeringRecommendation(
                    id=f"erec-{uuid.uuid4()}",
                    recommendation_type="reuse_genome",
                    description="Prefer existing 'payments' ArchitectureGenome to standard custom stripe connector scripts.",
                    confidence=0.95,
                    governing_principle_id="plugin_first"
                )
            )

        # 2. Add advisory fixes for flagged anti-patterns
        for ap in violated_antipatterns:
            recs.append(
                EngineeringRecommendation(
                    id=f"erec-{uuid.uuid4()}",
                    recommendation_type="avoid_antipattern",
                    description=f"Avoid historical anti-pattern '{ap.name}'. Remedy: {ap.remedy}",
                    confidence=0.85
                )
            )

        return recs
