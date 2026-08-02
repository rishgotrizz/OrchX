import sys
import argparse
from orchx_core.architecture.validator import ArchitectureConsistencyValidator

def main():
    parser = argparse.ArgumentParser(description="OrchX Architecture Protection System")
    parser.add_argument("--core", default="orchx_core.interfaces", help="Core interfaces package")
    parser.add_argument("--runtime", default="orchx_runtime", help="Runtime implementation package")
    
    args = parser.parse_args()
    
    print("Running Architecture Validation...")
    validator = ArchitectureConsistencyValidator(core_pkg=args.core, runtime_pkg=args.runtime)
    
    if validator.validate_all():
        print("✅ Architecture validation passed. Contracts and dependencies are consistent.")
        sys.exit(0)
    else:
        print("❌ Architecture validation failed!")
        for error in validator.errors:
            print(f"  - {error}")
        sys.exit(1)

if __name__ == "__main__":
    main()
