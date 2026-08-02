import pytest
from typing import Dict, Any

from orchx_core.interfaces.review_contracts import ReviewSeverity, ReviewCategory
from orchx_runtime.review_rules import (
    SyntaxValidationRule,
    ArchitectureValidationRule,
    DocstringCompletenessRule
)
from orchx_runtime.review_manager import ReviewManager


# 1. Rule Metadata & Registries Tests
def test_review_manager_registration():
    manager = ReviewManager()
    syntax_rule = SyntaxValidationRule()
    
    manager.register_rule(syntax_rule)
    assert len(manager.list_rules()) == 1
    assert manager.list_rules()[0].metadata.rule_id == "rule-syntax-01"
    assert manager.list_rules()[0].metadata.category == ReviewCategory.CORRECTNESS


# 2. Pluggable Rules Evaluators Tests
def test_syntax_brackets_rule():
    rule = SyntaxValidationRule()
    
    # 1. Correct syntax
    f_ok = rule.evaluate("def test(): print('hello')", "test.py")
    assert len(f_ok) == 0

    # 2. Unclosed opening bracket
    f_err = rule.evaluate("def test(: print('hello')", "test.py")
    assert len(f_err) == 1
    assert "Unclosed opening bracket" in f_err[0].message
    assert f_err[0].severity == ReviewSeverity.CRITICAL
    assert f_err[0].evidence.location == "CharOffset:8"
    assert f_err[0].suggested_fix is not None
    assert "closing bracket" in f_err[0].suggested_fix.description


def test_architecture_imports_rule():
    rule = ArchitectureValidationRule()

    # Backend file importing react
    f_err = rule.evaluate("import react\ndef api_call(): pass", "backend/routes.py")
    assert len(f_err) == 1
    assert f_err[0].severity == ReviewSeverity.HIGH
    assert f_err[0].category == ReviewCategory.ARCHITECTURE
    assert "Illegal backend import" in f_err[0].message


def test_docstring_completeness_rule():
    rule = DocstringCompletenessRule()

    # Missing docstring header in python file
    f_err = rule.evaluate("def run(): pass", "main.py")
    assert len(f_err) == 1
    assert f_err[0].severity == ReviewSeverity.LOW
    assert f_err[0].category == ReviewCategory.DOCUMENTATION


# 3. Report Compilation and Score Budgeting Tests
def test_review_report_score_deductions():
    manager = ReviewManager()
    manager.register_rule(SyntaxValidationRule())
    manager.register_rule(ArchitectureValidationRule())
    manager.register_rule(DocstringCompletenessRule())

    # Code sample with unclosed brackets (CRITICAL - 25pts),
    # illegal imports (HIGH - 15pts), and missing docstrings (LOW - 1pts).
    bad_code = "import react\ndef test(: pass"
    
    report = manager.run_review("run-test-01", bad_code, "backend/core.py")

    assert report.total_findings == 3
    assert report.severity_breakdown[ReviewSeverity.CRITICAL] == 1
    assert report.severity_breakdown[ReviewSeverity.HIGH] == 1
    assert report.severity_breakdown[ReviewSeverity.LOW] == 1
    
    # Calculation: 100 - (25*1) - (15*1) - (1*1) = 59.0
    assert report.overall_score == 59.0
    assert len(report.recommendations) == 3
    assert len(report.failed_rules) == 3
