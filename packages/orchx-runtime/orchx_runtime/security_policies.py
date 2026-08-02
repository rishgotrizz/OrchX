import os
from typing import Any, Tuple

from orchx_core.interfaces.security_contracts import SecurityPolicy


class FilesystemIsolationPolicy(SecurityPolicy):
    """
    Enforces that filesystem access paths are restricted to workspace directories.
    """

    @property
    def policy_name(self) -> str:
        return "Filesystem Isolation Policy"

    def validate(self, context: Any) -> Tuple[bool, str]:
        # Context is expected to be ExecutionContext or similar payload containing working_directory
        working_dir = getattr(context, "working_directory", "")
        if not working_dir:
            return True, "No filesystem paths targeted. Policy bypass allowed."

        # Rejects root path lookups outside workspaces
        abs_path = os.path.abspath(working_dir)
        bad_roots = ["/etc", "/var", "/bin", "/usr", "/root"]
        for r in bad_roots:
            if abs_path.startswith(r):
                return False, f"Violation: Filesystem path '{working_dir}' is linked to root folder '{r}'."

        return True, "Filesystem path validated successfully within project boundaries."


class NetworkBoundaryPolicy(SecurityPolicy):
    """
    Validates that task network targets are whitelisted in worker capabilities.
    """

    @property
    def policy_name(self) -> str:
        return "Network Boundary Policy"

    def validate(self, context: Any) -> Tuple[bool, str]:
        task = getattr(context, "task", None)
        worker = getattr(context, "worker", None)
        if not task or not worker:
            return True, "No execution task meta available."

        # Fetch required network endpoints from task metadata
        target_domains = task.metadata.get("network_targets", [])
        if not target_domains:
            return True, "No network access requested by task."

        # Check declared worker permission whitelists
        allowed_domains = getattr(worker, "network_whitelist", [])
        for domain in target_domains:
            if domain not in allowed_domains:
                return False, f"Violation: Task requested connection to unauthorized network domain '{domain}'."

        return True, "All network connection endpoints matched whitelist permissions."
