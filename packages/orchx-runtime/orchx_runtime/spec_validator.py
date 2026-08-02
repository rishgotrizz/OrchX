from typing import Dict, List, Any, Set


from orchx_core.interfaces.spec import ProductSpecification, Requirement


class ProductSpecificationValidator:
    """
    Validates ProductSpecification values, conflicting constraints, 
    unsupported platforms, and circular dependencies in requirements.
    """

    @staticmethod
    def validate(spec: ProductSpecification) -> List[Dict[str, Any]]:
        errors = []

        # 1. Check required fields
        if not spec.project_name.strip():
            errors.append({
                "error_type": "MISSING_FIELD",
                "message": "Project name cannot be empty.",
                "ref_field": "project_name"
            })
        if len(spec.project_description.strip()) < 10:
            errors.append({
                "error_type": "INVALID_FIELD",
                "message": "Project description must be at least 10 characters long.",
                "ref_field": "project_description"
            })

        # 2. Check empty acceptance criteria
        if not spec.acceptance_criteria:
            errors.append({
                "error_type": "MISSING_ACCEPTANCE_CRITERIA",
                "message": "Specification must contain at least one acceptance criterion.",
                "ref_field": "acceptance_criteria"
            })

        # 3. Check conflicting tech and platform constraints
        techs = [t.lower() for t in spec.technology_preferences]
        platforms = [p.lower() for p in spec.target_platforms]

        if "swift" in techs and "ios" not in platforms and "macos" not in platforms:
            errors.append({
                "error_type": "CONFLICTING_CONSTRAINTS",
                "message": "Technology preference Swift/SwiftUI requires iOS or macOS platforms.",
                "ref_field": "technology_preferences"
            })

        if "kotlin" in techs and "android" not in platforms:
            errors.append({
                "error_type": "CONFLICTING_CONSTRAINTS",
                "message": "Technology preference Kotlin requires Android platform.",
                "ref_field": "technology_preferences"
            })

        # 4. Check circular dependencies in requirements
        all_reqs: List[Requirement] = []
        all_reqs.extend(spec.requirements.functional)
        all_reqs.extend(spec.requirements.non_functional)
        all_reqs.extend(spec.requirements.security)
        all_reqs.extend(spec.requirements.performance)
        all_reqs.extend(spec.requirements.ux)
        all_reqs.extend(spec.requirements.deployment)
        all_reqs.extend(spec.requirements.testing)
        all_reqs.extend(spec.requirements.documentation)

        req_ids = {r.id for r in all_reqs}
        adj = {}
        for r in all_reqs:
            deps = r.metadata.get("dependencies", [])
            adj[r.id] = [d for d in deps if d in req_ids]

        visited = {}  # 0=unvisited, 1=visiting, 2=visited
        path = []

        def dfs(node):
            visited[node] = 1
            path.append(node)
            for neighbor in adj.get(node, []):
                if visited.get(neighbor, 0) == 1:
                    cycle_start = path.index(neighbor)
                    return path[cycle_start:] + [neighbor]
                if visited.get(neighbor, 0) == 0:
                    res = dfs(neighbor)
                    if res:
                        return res
            path.pop()
            visited[node] = 2
            return None

        for r in all_reqs:
            if visited.get(r.id, 0) == 0:
                cycle = dfs(r.id)
                if cycle:
                    errors.append({
                        "error_type": "CIRCULAR_DEPENDENCY",
                        "message": f"Circular dependency detected in requirements: {' -> '.join(cycle)}",
                        "ref_field": "requirements"
                    })
                    break

        return errors
