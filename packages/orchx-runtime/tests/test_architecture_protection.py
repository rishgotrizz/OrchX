import pytest
from orchx_core.architecture.validator import ArchitectureConsistencyValidator
import importlib
import sys

def test_architecture_validator_instantiation():
    validator = ArchitectureConsistencyValidator()
    assert validator.core_pkg == "orchx_core.interfaces"
    assert validator.runtime_pkg == "orchx_runtime"

def test_no_circular_dependencies():
    # If this fails, it means there is a circular dependency in orchx_runtime
    validator = ArchitectureConsistencyValidator()
    validator._validate_circular_dependencies()
    assert len(validator.errors) == 0, f"Circular dependencies found: {validator.errors}"

def test_implementation_compliance():
    # Tests whether orchx_runtime properly implements orchx_core.interfaces ABCs
    validator = ArchitectureConsistencyValidator()
    validator._validate_implementations()
    # Log errors for debugging if the test fails
    if len(validator.errors) > 0:
        for err in validator.errors:
            print(err)
    
    # We should expect 0 errors if everything is compliant.
    # Note: If there are existing compliance issues, this will catch them!
    # Currently setting it to just run without asserting 0 errors if the codebase is not 100% compliant yet,
    # but the instructions say "Maintain a minimum passing rate of 100%". So we will assert 0.
    assert len(validator.errors) == 0, f"Compliance errors found: {validator.errors}"

def test_validate_all():
    validator = ArchitectureConsistencyValidator()
    is_valid = validator.validate_all()
    assert is_valid is True
    assert len(validator.errors) == 0
