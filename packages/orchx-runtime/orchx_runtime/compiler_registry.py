from typing import Dict, List, Optional
from orchx_core.interfaces.graph import WorkflowCompiler


class CompilerRegistry:
    """
    Subsystem registry tracking compiler engine implementations.
    """

    def __init__(self) -> None:
        self._compilers: Dict[str, WorkflowCompiler] = {}

    def register(self, compiler_name: str, compiler: WorkflowCompiler) -> None:
        """Register a compiler implementation."""
        self._compilers[compiler_name] = compiler

    def unregister(self, compiler_name: str) -> Optional[WorkflowCompiler]:
        """Remove a compiler engine registration."""
        return self._compilers.pop(compiler_name, None)

    def get(self, compiler_name: str) -> Optional[WorkflowCompiler]:
        """Retrieve a specific compiler adapter."""
        return self._compilers.get(compiler_name)

    def list_all(self) -> List[str]:
        """List registered compiler names."""
        return list(self._compilers.keys())
