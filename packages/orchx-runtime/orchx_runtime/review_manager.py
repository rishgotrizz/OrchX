import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from orchx_core.interfaces.review_contracts import (
    ReviewRule,
    ReviewFinding,
    ReviewReport,
    ReviewSeverity,
)


class ReviewManager:
    """
    Subsystem registry managing rules evaluations and report statistics compiles.
    """

    def __init__(self) -> None:
        self._rules: List[ReviewRule] = []

    def register_rule(self, rule: ReviewRule) -> None:
        """Register a validation review rule."""
        self._rules.append(rule)

    def unregister_rule(self, rule_id: str) -> Optional[ReviewRule]:
        """Remove a rule registration."""
        for r in self._rules:
            if r.metadata.rule_id == rule_id:
                self._rules.remove(r)
                return r
        return None

    def list_rules(self) -> List[ReviewRule]:
        """List registered rules."""
        return self._rules

    def run_review(self, target_id: str, content: str, target_name: str) -> ReviewReport:
        """
        Evaluate target content against active rules and generate the report.
        """
        all_findings: List[ReviewFinding] = []
        passed_rules: List[str] = []
        failed_rules: List[str] = []

        # 1. Run evaluations
        for rule in self._rules:
            if not rule.metadata.enabled:
                continue

            findings = rule.evaluate(content, target_name)
            if findings:
                all_findings.extend(findings)
                failed_rules.append(rule.metadata.rule_id)
            else:
                passed_rules.append(rule.metadata.rule_id)

        # 2. Compute severity breakdown and counts
        severity_breakdown: Dict[ReviewSeverity, int] = {
            ReviewSeverity.CRITICAL: 0,
            ReviewSeverity.HIGH: 0,
            ReviewSeverity.MEDIUM: 0,
            ReviewSeverity.LOW: 0,
            ReviewSeverity.INFO: 0
        }
        for f in all_findings:
            severity_breakdown[f.severity] = severity_breakdown.get(f.severity, 0) + 1

        # 3. Calculate summary score (baseline 100.0, deduct based on severities)
        overall_score = 100.0
        deductions = {
            ReviewSeverity.CRITICAL: 25.0,
            ReviewSeverity.HIGH: 15.0,
            ReviewSeverity.MEDIUM: 5.0,
            ReviewSeverity.LOW: 1.0,
            ReviewSeverity.INFO: 1.0
        }
        for sev, count in severity_breakdown.items():
            overall_score -= deductions.get(sev, 1.0) * count

        # Cap score floor at 0.0
        overall_score = max(0.0, overall_score)

        # 4. Extract recommendations list
        recommendations = []
        for f in all_findings:
            if f.suggested_fix:
                recommendations.append(f.suggested_fix.description)

        # 5. Assemble final report
        return ReviewReport(
            review_id=f"review-{uuid.uuid4()}",
            target_id=target_id,
            findings=all_findings,
            summary=f"Review completed. Generated {len(all_findings)} issues across {len(self._rules)} rules.",
            overall_score=overall_score,
            severity_breakdown=severity_breakdown,
            total_findings=len(all_findings),
            passed_rules=passed_rules,
            failed_rules=failed_rules,
            recommendations=recommendations
        )
