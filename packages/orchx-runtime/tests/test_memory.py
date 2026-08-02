import pytest
from datetime import datetime, timedelta, timezone

from orchx_core.interfaces.memory_contracts import (
    MemoryProvenance,
    MemoryImportance,
    MemoryRelationship,
    WorkingMemory,
    SessionMemory,
    ProjectMemory,
    KnowledgeMemory,
    ContextBudget
)
from orchx_runtime.memory_engine import (
    LayeredMemoryRegistry,
    RecentRetrieval,
    SemanticRetrieval,
    ContextBuilder
)


# 1. Provenance Validation Tests
def test_provenance_validation():
    registry = LayeredMemoryRegistry()
    
    # Missing project_id / session_id
    prov_invalid = MemoryProvenance(
        memory_id="mem-1",
        created_by="agent",
        project_id="",
        session_id=""
    )
    
    mem = WorkingMemory(
        id="m1",
        content="Invalid memory",
        provenance=prov_invalid,
        importance=MemoryImportance.NORMAL
    )

    with pytest.raises(ValueError) as excinfo:
        registry.store(mem)
    
    assert "Provenance validation failed" in str(excinfo.value)


# 2. Layer Isolation and Expiration Policies
def test_layered_isolation_and_expiration():
    registry = LayeredMemoryRegistry()
    
    prov = MemoryProvenance(
        memory_id="mem-2",
        created_by="agent-coder",
        project_id="p-101",
        session_id="s-202"
    )

    # Active memory
    m_working = WorkingMemory(
        id="m_work",
        content="Active working memory",
        provenance=prov
    )
    # Expired memory
    m_expired = SessionMemory(
        id="m_sess",
        content="Expired session memory",
        provenance=prov,
        expires_at=datetime.now(timezone.utc) - timedelta(seconds=10)
    )

    registry.store(m_working)
    registry.store(m_expired)

    # Check isolation
    assert len(registry.list_layer("working")) == 1
    # Expired is filtered out
    assert len(registry.list_layer("session")) == 0
    assert len(registry.list_all()) == 1


# 3. Memory Relationships Validation
def test_memory_relationships():
    prov = MemoryProvenance(
        memory_id="mem-3",
        created_by="agent-planner",
        project_id="p-101",
        session_id="s-202"
    )

    m1 = ProjectMemory(
        id="spec-v1",
        content="Requirements spec v1",
        provenance=prov
    )
    
    m2 = ProjectMemory(
        id="spec-v2",
        content="Requirements spec v2",
        provenance=prov,
        relationships=[
            MemoryRelationship(
                source_id="spec-v2",
                target_id="spec-v1",
                relationship_type="replaces"
            )
        ]
    )

    assert len(m2.relationships) == 1
    assert m2.relationships[0].relationship_type == "replaces"
    assert m2.relationships[0].target_id == "spec-v1"


# 4. Pluggable Retrieval Strategies Tests
def test_retrieval_strategies():
    prov1 = MemoryProvenance(
        memory_id="mem-1",
        created_by="agent",
        project_id="p-1",
        session_id="s-1",
        created_at=datetime.now(timezone.utc) - timedelta(minutes=10)
    )
    
    prov2 = MemoryProvenance(
        memory_id="mem-2",
        created_by="agent",
        project_id="p-1",
        session_id="s-1",
        created_at=datetime.now(timezone.utc)
    )

    m1 = KnowledgeMemory(id="k1", content="Python lists tutorial", provenance=prov1)
    m2 = KnowledgeMemory(id="k2", content="Golang interfaces documentation", provenance=prov2)

    memories = [m1, m2]

    # 1. Recent Retrieval (sorts by created_at desc)
    recent = RecentRetrieval()
    res_recent = recent.retrieve("Golang", memories)
    assert res_recent[0].id == "k2"  # Golang is newer

    # 2. Semantic Retrieval (checks query overlaps)
    semantic = SemanticRetrieval()
    res_semantic = semantic.retrieve("Python lists", memories)
    assert res_semantic[0].id == "k1"  # matches Python lists


# 5. Context Builder & Token Budgets
def test_context_builder_budgeting():
    prov = MemoryProvenance(
        memory_id="m",
        created_by="agent",
        project_id="p-1",
        session_id="s-1"
    )

    m1 = WorkingMemory(
        id="w1",
        content="Important API credentials settings key",
        provenance=prov,
        importance=MemoryImportance.CRITICAL
    )
    m2 = WorkingMemory(
        id="w2",
        content="General comments debug lines",
        provenance=prov,
        importance=MemoryImportance.LOW
    )

    memories = [m2, m1]
    builder = ContextBuilder()

    # 1. Budget by Importance Prioritization
    budget_importance = ContextBudget(
        maximum_tokens=2048,
        maximum_memory_objects=10,
        prioritization_strategy="importance",
        compression_strategy="truncate"
    )
    
    ctx = builder.build_context(memories, budget_importance)
    # Important should be placed first
    assert "Important API credentials settings key" in ctx
    assert ctx.startswith("[Memory Context]\n- Important API credentials")

    # 2. Budget by maximum token limitation
    # Let's set a small maximum_tokens budget to force truncation
    budget_tight = ContextBudget(
        maximum_tokens=10,  # ~40 characters limit
        maximum_memory_objects=10,
        prioritization_strategy="importance",
        compression_strategy="truncate"
    )
    
    ctx_tight = builder.build_context(memories, budget_tight)
    # The first item "Important API credentials settings key" is len 40 -> 10 tokens.
    # The second item will exceed maximum_tokens, so it gets dropped/truncated
    assert "General comments debug lines" not in ctx_tight
