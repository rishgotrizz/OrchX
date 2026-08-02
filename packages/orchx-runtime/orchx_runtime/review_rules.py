import uuid
from typing import List

from orchx_core.interfaces.review_contracts import (
    ReviewRule,
    ReviewRuleMetadata,
    ReviewCategory,
    ReviewSeverity,
    ReviewFinding,
    ReviewEvidence,
    SuggestedFix,
)


class SyntaxValidationRule(ReviewRule):
    """
    Validates structural correctness of code files (e.g. unclosed brackets).
    """

    @property
    def metadata(self) -> ReviewRuleMetadata:
        return ReviewRuleMetadata(
            rule_id="rule-syntax-01",
            name="Syntax Brackets Validator",
            version="1.0.0",
            category=ReviewCategory.CORRECTNESS,
            description="Verifies that all brackets are balanced in code strings."
        )

    def evaluate(self, content: str, target_name: str) -> List[ReviewFinding]:
        findings = []
        open_brackets = {"(": ")", "{": "}", "[": "]"}
        stack = []
        
        for idx, char in enumerate(content):
            if char in open_brackets:
                stack.append((char, idx))
            elif char in open_brackets.values():
                if not stack:
                    # Unopened closing bracket
                    findings.append(
                        self._create_finding(
                            target_name,
                            idx,
                            char,
                            f"Unopened closing bracket '{char}' detected."
                        )
                    )
                else:
                    last_open, _ = stack.pop()
                    if open_brackets[last_open] != char:
                        findings.append(
                            self._create_finding(
                                target_name,
                                idx,
                                char,
                                f"Mismatched closing bracket '{char}' for opening '{last_open}'."
                            )
                        )
        
        # Remaining unclosed
        for open_char, idx in stack:
            findings.append(
                self._create_finding(
                    target_name,
                    idx,
                    open_char,
                    f"Unclosed opening bracket '{open_char}' detected.",
                    suggested_close=open_brackets[open_char]
                )
            )

        return findings

    def _create_finding(self, target_name: str, idx: int, char: str, msg: str, suggested_close: str = None) -> ReviewFinding:
        fix = None
        if suggested_close:
            fix = SuggestedFix(
                description=f"Append the corresponding closing bracket '{suggested_close}'",
                rationale="Mismatched or unclosed brackets cause compilation errors.",
                confidence=1.0,
                affected_artifacts=[target_name]
            )

        return ReviewFinding(
            id=f"finding-syntax-{uuid.uuid4()}",
            category=ReviewCategory.CORRECTNESS,
            severity=ReviewSeverity.CRITICAL,
            message=msg,
            evidence=ReviewEvidence(
                artifact_id=target_name,
                file_path=target_name,
                location=f"CharOffset:{idx}",
                snippet=char,
                explanation=msg
            ),
            suggested_fix=fix
        )


class ArchitectureValidationRule(ReviewRule):
    """
    Enforces architectural layering boundaries (e.g. backend files import frontend components).
    """

    @property
    def metadata(self) -> ReviewRuleMetadata:
        return ReviewRuleMetadata(
            rule_id="rule-arch-01",
            name="Backend Import Boundaries",
            version="1.0.0",
            category=ReviewCategory.ARCHITECTURE,
            description="Blocks backend modules from importing frontend frameworks."
        )

    def evaluate(self, content: str, target_name: str) -> List[ReviewFinding]:
        findings = []
        
        # Check if backend file imports frontend
        is_backend = any(x in target_name.lower() for x in ["backend", "runtime", "core"])
        if is_backend:
            illegal_imports = ["react", "vue", "three", "tailwind"]
            for imp in illegal_imports:
                if f"import {imp}" in content or f"from {imp} import" in content:
                    findings.append(
                        ReviewFinding(
                            id=f"finding-arch-{uuid.uuid4()}",
                            category=ReviewCategory.ARCHITECTURE,
                            severity=ReviewSeverity.HIGH,
                            message=f"Illegal backend import: Backend module imports frontend package '{imp}'.",
                            evidence=ReviewEvidence(
                                artifact_id=target_name,
                                file_path=target_name,
                                location="Imports",
                                snippet=f"import {imp}",
                                explanation="Improper layer architecture coupling. Backend files must remain UI agnostic."
                            ),
                            suggested_fix=SuggestedFix(
                                description=f"Remove frontend import '{imp}' and decouple logic using registries.",
                                rationale="Improves system modularity, reuse, and compilation boundaries.",
                                confidence=0.9
                            )
                        )
                    )
        
        return findings


class DocstringCompletenessRule(ReviewRule):
    """
    Checks python files for docstring comments.
    """

    @property
    def metadata(self) -> ReviewRuleMetadata:
        return ReviewRuleMetadata(
            rule_id="rule-docstring-01",
            name="Python Docstrings Completeness",
            version="1.0.0",
            category=ReviewCategory.DOCUMENTATION,
            description="Validates that python modules contain docstrings documentation."
        )

    def evaluate(self, content: str, target_name: str) -> List[ReviewFinding]:
        findings = []
        if target_name.endswith(".py") and '"""' not in content:
            findings.append(
                ReviewFinding(
                    id=f"finding-doc-{uuid.uuid4()}",
                    category=ReviewCategory.DOCUMENTATION,
                    severity=ReviewSeverity.LOW,
                    message="Python module lacks documentation docstrings.",
                    evidence=ReviewEvidence(
                        artifact_id=target_name,
                        file_path=target_name,
                        location="Header",
                        snippet="N/A",
                        explanation="Module does not contain triple-quote docstrings explaining purpose."
                    ),
                    suggested_fix=SuggestedFix(
                        description="Add a header docstring at the top of the file.",
                        rationale="Ensures codebase remains maintainable for downstream engineers.",
                        confidence=0.8
                    )
                )
            )
        return findings
