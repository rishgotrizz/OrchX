import uuid
from typing import Any, Dict, List
from orchx_core.interfaces.graph import ExecutionGraph, WorkflowCompiler
from orchx_core.interfaces.task import Task, Artifact, TaskState
from orchx_core.interfaces.workflow import WorkflowDefinition
from orchx_runtime.validator import WorkflowValidator


class DefaultWorkflowCompiler(WorkflowCompiler):
    """
    Synthesizes static WorkflowDefinitions and parameters into executable ExecutionGraphs.
    Guarantees stable immutable task identity rules via UUID generation.
    """

    async def compile(
        self,
        definition: WorkflowDefinition,
        inputs: Dict[str, Any],
        instance_id: str
    ) -> ExecutionGraph:
        """
        Compile definition steps and runtime inputs into an immutable ExecutionGraph.
        """
        # 1. Structural pre-validation check
        validation_errors = WorkflowValidator.validate_definition(definition)
        if validation_errors:
            raise ValueError(f"Workflow compilation failed due to template validation errors: {validation_errors}")

        nodes: Dict[str, Task] = {}
        edges: Dict[str, List[str]] = {}
        artifacts_registry: Dict[str, Artifact] = {}

        # 2. Map local template step IDs to concrete stable task UUIDs
        step_id_map = {step.id: f"task-{uuid.uuid4()}" for step in definition.steps}

        # 3. Process inputs: Instantiates input Artifacts supplied during compilation
        for input_key, val in inputs.items():
            if isinstance(val, Artifact):
                artifacts_registry[val.id] = val
            else:
                art_id = f"art-{instance_id}-input-{input_key}"
                artifacts_registry[art_id] = Artifact(
                    id=art_id,
                    name=input_key,
                    kind="parameter",
                    version="1.0.0",
                    metadata={"value": val}
                )

        # 4. Instantiate steps into concrete Tasks
        for step in definition.steps:
            concrete_task_id = step_id_map[step.id]
            
            # Map input port names to concrete Artifact IDs
            concrete_inputs = []
            for inp_port in step.inputs:
                # Find if a matching input artifact has been registered
                matching_art = next(
                    (art for art in artifacts_registry.values() if art.name == inp_port), None
                )
                if matching_art:
                    # Register this task as a consumer
                    if concrete_task_id not in matching_art.consumer_task_ids:
                        matching_art.consumer_task_ids.append(concrete_task_id)
                    concrete_inputs.append(matching_art.id)
                else:
                    # Create generic placeholder input artifact if not already registered
                    art_id = f"art-{instance_id}-{step.id}-input-{inp_port}"
                    # Determine expected kind
                    expected_kind = step.expected_input_kinds.get(inp_port, "generic_data")
                    
                    artifacts_registry[art_id] = Artifact(
                        id=art_id,
                        name=inp_port,
                        kind=expected_kind,
                        version="1.0.0",
                        consumer_task_ids=[concrete_task_id]
                    )
                    concrete_inputs.append(art_id)

            # Map output port names to concrete output Artifacts produced by this task
            concrete_outputs = []
            for out_port in step.outputs:
                art_id = f"art-{instance_id}-{step.id}-output-{out_port}"
                output_artifact = Artifact(
                    id=art_id,
                    name=out_port,
                    kind="generic_data", # Outputs are generic until runtime updates
                    version="1.0.0",
                    producer_task_id=concrete_task_id
                )
                artifacts_registry[art_id] = output_artifact
                concrete_outputs.append(art_id)

            # Map step dependencies to concrete task dependencies
            concrete_deps = [step_id_map[dep] for dep in step.dependencies if dep in step_id_map]

            task_instance = Task(
                id=concrete_task_id,
                name=step.name,
                type=step.type,
                description=step.description,
                status=TaskState.CREATED,
                priority=step.priority,
                inputs=concrete_inputs,
                outputs=concrete_outputs,
                dependencies=concrete_deps,
                required_capabilities=step.required_capabilities,
                required_tools=step.required_tools,
                preferred_provider=step.preferred_provider,
                preferred_agent=step.preferred_agent,
                retry_policy=step.retry_policy,
                timeout=step.timeout,
                expected_input_kinds=step.expected_input_kinds.copy(),
                constraints=step.constraints,
                resources=step.resources,
                metadata=step.metadata.copy()
            )

            nodes[concrete_task_id] = task_instance
            edges[concrete_task_id] = concrete_deps

        return ExecutionGraph(
            workflow_instance_id=instance_id,
            nodes=nodes,
            edges=edges,
            artifacts=artifacts_registry
        )
