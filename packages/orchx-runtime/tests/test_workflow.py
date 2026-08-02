import pytest
from typing import Dict, Any

from orchx_core.interfaces.task import Task, Artifact, TaskState, TaskPriority
from orchx_core.interfaces.workflow import WorkflowDefinition, TaskDefinition, WorkflowInstance
from orchx_core.interfaces.graph import ExecutionGraph
from orchx_runtime.validator import WorkflowValidator
from orchx_runtime.compiler import DefaultWorkflowCompiler
from orchx_runtime.workflow_template_registry import WorkflowTemplateRegistry
from orchx_runtime.task_type_registry import TaskTypeRegistry
from orchx_runtime.execution_graph_registry import ExecutionGraphRegistry
from orchx_runtime.compiler_registry import CompilerRegistry


# 1. Template Validation Tests
def test_workflow_definition_duplicate_ids():
    definition = WorkflowDefinition(
        id="wf-dup",
        name="Duplicate steps",
        steps=[
            TaskDefinition(id="step-1", name="Step 1", type="test"),
            TaskDefinition(id="step-1", name="Step 1 Dup", type="test")
        ]
    )
    
    errors = WorkflowValidator.validate_definition(definition)
    assert len(errors) == 1
    assert errors[0]["error_type"] == "DUPLICATE_STEP_ID"


def test_workflow_definition_missing_dependency():
    definition = WorkflowDefinition(
        id="wf-missing",
        name="Missing dependency step",
        steps=[
            TaskDefinition(id="step-1", name="Step 1", type="test", dependencies=["step-nonexistent"])
        ]
    )
    
    errors = WorkflowValidator.validate_definition(definition)
    assert len(errors) == 1
    assert errors[0]["error_type"] == "MISSING_DEPENDENCY"


def test_workflow_definition_circular_dependency():
    definition = WorkflowDefinition(
        id="wf-cycle",
        name="Cyclic steps",
        steps=[
            TaskDefinition(id="step-1", name="Step 1", type="test", dependencies=["step-2"]),
            TaskDefinition(id="step-2", name="Step 2", type="test", dependencies=["step-1"])
        ]
    )
    
    errors = WorkflowValidator.validate_definition(definition)
    assert len(errors) == 1
    assert errors[0]["error_type"] == "CIRCULAR_DEPENDENCY"
    assert "step-1" in errors[0]["message"]


def test_workflow_definition_unauthorized_capability():
    definition = WorkflowDefinition(
        id="wf-cap",
        name="Cap check",
        required_capabilities=["filesystem.read"],
        steps=[
            TaskDefinition(
                id="step-1",
                name="Step 1",
                type="test",
                required_capabilities=["filesystem.write"]  # Not in parent workflow
            )
        ]
    )
    
    errors = WorkflowValidator.validate_definition(definition)
    assert len(errors) == 1
    assert errors[0]["error_type"] == "UNAUTHORIZED_CAPABILITY"


# 2. Compilation Tests
@pytest.mark.asyncio
async def test_workflow_compiler_and_artifacts():
    definition = WorkflowDefinition(
        id="wf-website",
        name="SaaS Builder Workflow",
        required_capabilities=["filesystem.read", "filesystem.write"],
        steps=[
            TaskDefinition(
                id="clone-repo",
                name="Clone Repo",
                type="git_clone",
                inputs=["git_url"],
                outputs=["codebase"],
                required_capabilities=["filesystem.write"]
            ),
            TaskDefinition(
                id="lint-code",
                name="Lint Codebase",
                type="eslint",
                inputs=["codebase"],
                outputs=["lint_report"],
                dependencies=["clone-repo"],
                required_capabilities=["filesystem.read"],
                expected_input_kinds={"codebase": "source_code"}
            )
        ]
    )

    compiler = DefaultWorkflowCompiler()
    inputs = {"git_url": "https://github.com/orchx/saas.git"}
    
    graph = await compiler.compile(definition, inputs, "run-website-01")
    
    # Verify graph outputs
    assert graph.workflow_instance_id == "run-website-01"
    assert len(graph.nodes) == 2
    
    # Find tasks by name
    clone_task = next(t for t in graph.nodes.values() if t.name == "Clone Repo")
    lint_task = next(t for t in graph.nodes.values() if t.name == "Lint Codebase")
    
    assert clone_task.id.startswith("task-")
    assert lint_task.id.startswith("task-")

    # Verify dependency mapping
    assert graph.edges[lint_task.id] == [clone_task.id]

    # Verify input parameter conversion into Artifact
    art_input = next(a for a in graph.artifacts.values() if a.name == "git_url")
    assert art_input.kind == "parameter"
    
    # Verify output connection linked as input to downstream
    codebase_art = next(a for a in graph.artifacts.values() if a.name == "codebase")
    assert codebase_art.producer_task_id == clone_task.id
    
    # Downstream task should consume codebase_art.id and be tracked as consumer
    assert codebase_art.id in lint_task.inputs
    assert lint_task.id in codebase_art.consumer_task_ids


@pytest.mark.asyncio
async def test_incompatible_artifact_kinds():
    graph = ExecutionGraph(
        workflow_instance_id="run-compat-01",
        nodes={
            "t1": Task(
                id="t1",
                name="Task 1",
                type="test",
                inputs=["a1"],
                expected_input_kinds={"a1": "python_source"}  # Expects python_source
            )
        },
        edges={"t1": []},
        artifacts={
            # Artifact is parameters kind
            "a1": Artifact(id="a1", name="a1", kind="parameter")
        }
    )

    errors = WorkflowValidator.validate_graph(graph)
    assert len(errors) == 1
    assert errors[0]["error_type"] == "INCOMPATIBLE_ARTIFACT_KIND"
    assert "expects input artifact 'a1' to be of kind 'python_source', but got 'parameter'" in errors[0]["message"]


# 3. Serialization Tests
@pytest.mark.asyncio
async def test_execution_graph_serialization():
    graph = ExecutionGraph(
        workflow_instance_id="run-serial-01",
        nodes={
            "t1": Task(id="t1", name="Task 1", type="test", inputs=["a1"])
        },
        edges={"t1": []},
        artifacts={
            "a1": Artifact(id="a1", name="a1", kind="parameter")
        }
    )

    json_str = graph.to_json()
    assert '"workflow_instance_id": "run-serial-01"' in json_str

    yaml_str = graph.to_yaml()
    assert "workflow_instance_id: run-serial-01" in yaml_str


# 4. Registries Tests
def test_subsystem_registries():
    # WorkflowTemplateRegistry
    w_reg = WorkflowTemplateRegistry()
    template = WorkflowDefinition(id="t1", name="T1", steps=[])
    w_reg.register(template)
    assert w_reg.get("t1").name == "T1"
    assert len(w_reg.list_all()) == 1

    # TaskTypeRegistry
    t_reg = TaskTypeRegistry()
    t_reg.register("eslint", {"inputs": ["codebase"]})
    assert "eslint" in t_reg.list_all()

    # CompilerRegistry
    c_reg = CompilerRegistry()
    compiler = DefaultWorkflowCompiler()
    c_reg.register("default", compiler)
    assert c_reg.get("default") == compiler
