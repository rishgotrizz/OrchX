from typing import Dict, List, Any, Set, Optional
from orchx_core.interfaces.graph import ExecutionGraph
from orchx_core.interfaces.workflow import WorkflowDefinition, TaskDefinition


class WorkflowValidator:
    """
    Validates structural integrity, dependency cycles, capabilities, 
    and parameters across definitions and compiled execution graphs.
    """

    @staticmethod
    def validate_definition(definition: WorkflowDefinition) -> List[Dict[str, Any]]:
        """
        Scan a WorkflowDefinition for structural schema violations.
        """
        errors = []
        step_ids = [step.id for step in definition.steps]

        # 1. Check duplicate IDs
        if len(step_ids) != len(set(step_ids)):
            seen = set()
            duplicates = [x for x in step_ids if x in seen or seen.add(x)]
            errors.append({
                "error_type": "DUPLICATE_STEP_ID",
                "message": f"Workflow step templates contain duplicate identifiers: {duplicates}",
                "ref_id": definition.id
            })

        # 2. Check missing dependencies
        for step in definition.steps:
            for dep in step.dependencies:
                if dep not in step_ids:
                    errors.append({
                        "error_type": "MISSING_DEPENDENCY",
                        "message": f"Step '{step.id}' depends on undefined step template '{dep}'.",
                        "ref_id": step.id
                    })

        # 3. Check circular dependencies
        if not errors:
            cycle = WorkflowValidator._find_definition_cycle(definition.steps)
            if cycle:
                errors.append({
                    "error_type": "CIRCULAR_DEPENDENCY",
                    "message": f"Workflow definition contains circular dependencies: {' -> '.join(cycle)}",
                    "ref_id": definition.id
                })

        # 4. Check capability declarations
        workflow_caps = set(definition.required_capabilities)
        for step in definition.steps:
            for cap in step.required_capabilities:
                if cap not in workflow_caps:
                    errors.append({
                        "error_type": "UNAUTHORIZED_CAPABILITY",
                        "message": f"Step '{step.id}' requests capability '{cap}' which is not declared in the top-level workflow manifest.",
                        "ref_id": step.id
                    })

        return errors

    @staticmethod
    def validate_graph(graph: ExecutionGraph) -> List[Dict[str, Any]]:
        """
        Scan a compiled ExecutionGraph for runtime execution violations.
        """
        errors = []
        node_ids = set(graph.nodes.keys())

        # 1. Validate edge references
        for node_id, deps in graph.edges.items():
            if node_id not in node_ids:
                errors.append({
                    "error_type": "INVALID_GRAPH_EDGE",
                    "message": f"Dependency edge maps from non-existent node '{node_id}'.",
                    "ref_id": node_id
                })
            for dep in deps:
                if dep not in node_ids:
                    errors.append({
                        "error_type": "INVALID_GRAPH_EDGE",
                        "message": f"Node '{node_id}' references missing dependency task '{dep}'.",
                        "ref_id": node_id
                    })

        # 2. Check circular dependencies in graph
        if not errors:
            cycle = WorkflowValidator._find_graph_cycle(graph)
            if cycle:
                errors.append({
                    "error_type": "CIRCULAR_DEPENDENCY",
                    "message": f"Compiled execution graph contains cyclic loop dependencies: {' -> '.join(cycle)}",
                    "ref_id": graph.workflow_instance_id
                })

        # 3. Verify Artifact connections
        for task_id, task in graph.nodes.items():
            for inp_art_id in task.inputs:
                if inp_art_id not in graph.artifacts:
                    errors.append({
                        "error_type": "MISSING_INPUT_ARTIFACT",
                        "message": f"Task '{task_id}' consumes input artifact '{inp_art_id}' which is not registered in the graph context.",
                        "ref_id": task_id
                    })
                else:
                    artifact = graph.artifacts[inp_art_id]
                    # Verify kind compatibility matching expected kinds
                    expected_kind = task.expected_input_kinds.get(artifact.name)
                    if expected_kind and artifact.kind != expected_kind:
                        errors.append({
                            "error_type": "INCOMPATIBLE_ARTIFACT_KIND",
                            "message": f"Task '{task_id}' expects input artifact '{artifact.name}' to be of kind '{expected_kind}', but got '{artifact.kind}'.",
                            "ref_id": task_id
                        })
            for out_art_id in task.outputs:
                if out_art_id not in graph.artifacts:
                    errors.append({
                        "error_type": "MISSING_OUTPUT_ARTIFACT",
                        "message": f"Task '{task_id}' produces output artifact '{out_art_id}' which is not registered in the graph context.",
                        "ref_id": task_id
                    })

        return errors

    @staticmethod
    def _find_definition_cycle(steps: List[TaskDefinition]) -> Optional[List[str]]:
        adj = {step.id: step.dependencies for step in steps}
        visited: Dict[str, int] = {}  # 0=unvisited, 1=visiting, 2=visited
        path = []

        def dfs(node):
            visited[node] = 1
            path.append(node)
            for neighbor in adj.get(node, []):
                if neighbor not in adj:
                    continue  # Missing dep handled separately
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

        for step in steps:
            if visited.get(step.id, 0) == 0:
                cycle = dfs(step.id)
                if cycle:
                    return cycle
        return None

    @staticmethod
    def _find_graph_cycle(graph: ExecutionGraph) -> Optional[List[str]]:
        adj = graph.edges
        visited: Dict[str, int] = {}
        path = []

        def dfs(node):
            visited[node] = 1
            path.append(node)
            for neighbor in adj.get(node, []):
                if neighbor not in graph.nodes:
                    continue
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

        for node_id in graph.nodes:
            if visited.get(node_id, 0) == 0:
                cycle = dfs(node_id)
                if cycle:
                    return cycle
        return None
