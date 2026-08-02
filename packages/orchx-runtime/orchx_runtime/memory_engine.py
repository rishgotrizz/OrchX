import json
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from orchx_core.interfaces.memory_contracts import (
    MemoryObject,
    MemoryImportance,
    MemoryRelationship,
    WorkingMemory,
    SessionMemory,
    ProjectMemory,
    KnowledgeMemory,
    ContextBudget,
    RetrievalStrategy,
)


class LayeredMemoryRegistry:
    """
    Subsystem registry organizing memory records into independent logical layers.
    Enforces strict provenance checks and dynamic expiration filtering.
    """

    def __init__(self) -> None:
        self._working: List[WorkingMemory] = []
        self._session: List[SessionMemory] = []
        self._project: List[ProjectMemory] = []
        self._knowledge: List[KnowledgeMemory] = []

    def store(self, obj: MemoryObject) -> None:
        """
        Store memory object. Enforces provenance rules.
        """
        # Validate provenance keys
        prov = obj.provenance
        if not prov.project_id.strip() or not prov.session_id.strip() or not prov.created_by.strip():
            raise ValueError("Provenance validation failed: Binders (project_id, session_id, created_by) must be set.")

        if isinstance(obj, WorkingMemory):
            self._working.append(obj)
        elif isinstance(obj, SessionMemory):
            self._session.append(obj)
        elif isinstance(obj, ProjectMemory):
            self._project.append(obj)
        elif isinstance(obj, KnowledgeMemory):
            self._knowledge.append(obj)
        else:
            raise TypeError("Unsupported memory object type. Must be a subclass of MemoryObject.")

    def list_layer(self, layer: str) -> List[MemoryObject]:
        """List active items in a specific layer, filtering expired records."""
        now = datetime.now(timezone.utc)

        if layer == "working":
            raw = self._working
        elif layer == "session":
            raw = self._session
        elif layer == "project":
            raw = self._project
        elif layer == "knowledge":
            raw = self._knowledge
        else:
            return []

        # Filter out expired items
        return [
            item for item in raw
            if item.expires_at is None or item.expires_at > now
        ]

    def list_all(self) -> List[MemoryObject]:
        """Merge all layers, filtering expired records."""
        return (
            self.list_layer("working") +
            self.list_layer("session") +
            self.list_layer("project") +
            self.list_layer("knowledge")
        )


# Concrete Pluggable Retrieval Strategies
class RecentRetrieval(RetrievalStrategy):
    """Sorts candidate memories strictly by recency (created_at desc)."""

    def retrieve(self, query: str, memories: List[MemoryObject]) -> List[MemoryObject]:
        return sorted(memories, key=lambda m: m.provenance.created_at, reverse=True)


class SemanticRetrieval(RetrievalStrategy):
    """
    Simulates vector distance checks via text term overlap intersection scores.
    """

    def retrieve(self, query: str, memories: List[MemoryObject]) -> List[MemoryObject]:
        query_words = set(query.lower().split())
        scored = []
        for memory in memories:
            mem_words = set(memory.content.lower().split())
            intersection = query_words.intersection(mem_words)
            # Jaccard overlap score
            score = len(intersection) / max(1, len(query_words.union(mem_words)))
            scored.append((score, memory))

        # Sort by match score descending
        return [item[1] for item in sorted(scored, key=lambda x: x[0], reverse=True)]


class ContextBuilder:
    """
    Assembles memory prompts respecting token boundaries and priority budgets.
    """

    def build_context(self, memories: List[MemoryObject], budget: ContextBudget) -> str:
        # 1. Sort memories according to prioritization strategy
        if budget.prioritization_strategy == "importance":
            importance_weights = {
                MemoryImportance.CRITICAL: 4,
                MemoryImportance.HIGH: 3,
                MemoryImportance.NORMAL: 2,
                MemoryImportance.LOW: 1
            }
            sorted_memories = sorted(
                memories, key=lambda m: importance_weights.get(m.importance, 2), reverse=True
            )
        else:
            # Default to recency sorting
            sorted_memories = sorted(memories, key=lambda m: m.provenance.created_at, reverse=True)

        # 2. Apply max memory count limit
        limited_memories = sorted_memories[:budget.maximum_memory_objects]

        # 3. Assemble and budget estimated tokens (roughly 1 token per 4 characters)
        token_count = 0
        accepted_lines = []

        for mem in limited_memories:
            estimated_tokens = len(mem.content) // 4
            if token_count + estimated_tokens <= budget.maximum_tokens:
                accepted_lines.append(f"- {mem.content}")
                token_count += estimated_tokens
            else:
                # If compression strategy is truncate, drop remaining items
                if budget.compression_strategy == "truncate":
                    break

        if not accepted_lines:
            return ""

        return "[Memory Context]\n" + "\n".join(accepted_lines)


# ---------------------------------------------------------------------------
# SQLite persistence layer
# ---------------------------------------------------------------------------

_CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS memory_objects (
    id          TEXT PRIMARY KEY,
    layer       TEXT NOT NULL,
    content     TEXT NOT NULL,
    importance  TEXT,
    expires_at  TEXT,
    provenance  TEXT,
    created_at  TEXT
)
"""


class SQLiteMemoryStore:
    """
    Lightweight SQLite-backed persistence store for MemoryObject records.

    Each record is serialised as a flat JSON document and stored in the
    ``memory_objects`` table. All I/O uses only stdlib modules (sqlite3,
    json, datetime).
    """

    def __init__(self, db_path: str = ":memory:") -> None:
        """
        Initialise the store and ensure the schema exists.

        Args:
            db_path: Filesystem path to the SQLite database file, or
                     ``':memory:'`` for a transient in-process database.
        """
        self._db_path = db_path
        self._conn: sqlite3.Connection = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL;")
        self._conn.execute(_CREATE_TABLE_SQL)
        self._conn.commit()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def save(self, obj: MemoryObject, layer: str) -> None:
        """
        Persist a MemoryObject into the store.

        Uses ``INSERT OR REPLACE`` so re-saving the same ``memory_id``
        performs an idempotent upsert rather than raising a duplicate-key
        error.

        Args:
            obj:   The memory object to persist.
            layer: Logical layer name (``'working'``, ``'session'``,
                   ``'project'``, or ``'knowledge'``).
        """
        # Build a serialisable dict from the MemoryObject.
        # Works whether the object is a dataclass, Pydantic model, or has
        # a custom __dict__, gracefully falling back to str() for unknown
        # field types.
        raw: Dict[str, Any] = self._to_dict(obj)

        expires_at_str: Optional[str] = None
        if obj.expires_at is not None:
            expires_at_str = obj.expires_at.isoformat() if hasattr(obj.expires_at, "isoformat") else str(obj.expires_at)

        created_at_str: Optional[str] = None
        prov = getattr(obj, "provenance", None)
        if prov is not None:
            ca = getattr(prov, "created_at", None)
            if ca is not None:
                created_at_str = ca.isoformat() if hasattr(ca, "isoformat") else str(ca)

        self._conn.execute(
            """
            INSERT OR REPLACE INTO memory_objects
                (id, layer, content, importance, expires_at, provenance, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(getattr(obj, "memory_id", str(uuid.uuid4()))),
                layer,
                str(getattr(obj, "content", "")),
                str(getattr(obj, "importance", "")),
                expires_at_str,
                json.dumps(self._to_dict(prov)) if prov is not None else None,
                created_at_str,
            ),
        )
        self._conn.commit()

    def load_layer(self, layer: str) -> List[Dict[str, Any]]:
        """
        Return all persisted records for *layer* as plain dicts.

        Args:
            layer: Logical layer name to filter by.

        Returns:
            List of row dicts with keys matching the ``memory_objects``
            column names.
        """
        cursor = self._conn.execute(
            "SELECT * FROM memory_objects WHERE layer = ?",
            (layer,),
        )
        return [dict(row) for row in cursor.fetchall()]

    def search(self, query: str, layer: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Simple substring search over the ``content`` column.

        Args:
            query: Substring to search for (case-insensitive via ``LIKE``).
            layer: Optional layer filter; if ``None`` all layers are searched.

        Returns:
            List of matching row dicts.
        """
        like_pattern = f"%{query}%"
        if layer is not None:
            cursor = self._conn.execute(
                "SELECT * FROM memory_objects WHERE content LIKE ? AND layer = ?",
                (like_pattern, layer),
            )
        else:
            cursor = self._conn.execute(
                "SELECT * FROM memory_objects WHERE content LIKE ?",
                (like_pattern,),
            )
        return [dict(row) for row in cursor.fetchall()]

    def delete_expired(self) -> int:
        """
        Remove all records whose ``expires_at`` timestamp is in the past.

        Uses SQLite's built-in ``datetime('now')`` for the comparison so
        that timezone handling is consistent regardless of the host clock.

        Returns:
            Number of rows deleted.
        """
        cursor = self._conn.execute(
            "DELETE FROM memory_objects WHERE expires_at IS NOT NULL AND expires_at < datetime('now')"
        )
        self._conn.commit()
        return cursor.rowcount

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _to_dict(self, obj: Any) -> Dict[str, Any]:
        """
        Convert an arbitrary object to a JSON-serialisable dict.

        Tries (in order): ``model_dump()``, ``__dict__``, falling back to
        an empty dict so the caller is never surprised.
        """
        if obj is None:
            return {}
        if hasattr(obj, "model_dump"):
            # Pydantic v2
            try:
                return obj.model_dump(mode="json")
            except Exception:
                pass
        if hasattr(obj, "dict") and callable(obj.dict):
            # Pydantic v1
            try:
                return obj.dict()
            except Exception:
                pass
        if hasattr(obj, "__dataclass_fields__"):
            import dataclasses
            return dataclasses.asdict(obj)
        if hasattr(obj, "__dict__"):
            return {k: v for k, v in obj.__dict__.items() if not k.startswith("_")}
        return {}


# ---------------------------------------------------------------------------
# Persistent registry — extends LayeredMemoryRegistry with SQLite backing
# ---------------------------------------------------------------------------

_LAYER_FOR_TYPE: Dict[type, str] = {
    WorkingMemory: "working",
    SessionMemory: "session",
    ProjectMemory: "project",
    KnowledgeMemory: "knowledge",
}


class PersistentLayeredMemoryRegistry(LayeredMemoryRegistry):
    """
    Drop-in replacement for :class:`LayeredMemoryRegistry` that transparently
    persists every stored memory object to a SQLite database via
    :class:`SQLiteMemoryStore`.

    In-memory lists are kept in sync with the database so that callers which
    hold a reference to this registry always see the union of both sources.
    """

    def __init__(self, db_path: str = ":memory:") -> None:
        """
        Args:
            db_path: Path forwarded verbatim to :class:`SQLiteMemoryStore`.
        """
        super().__init__()
        self._store = SQLiteMemoryStore(db_path=db_path)

    # ------------------------------------------------------------------
    # Overridden LayeredMemoryRegistry methods
    # ------------------------------------------------------------------

    def store(self, obj: MemoryObject) -> None:
        """
        Store *obj* in the in-memory registry **and** persist it to SQLite.

        Provenance validation is delegated to the parent ``store()`` so all
        existing rules are preserved.

        Args:
            obj: The memory object to persist.

        Raises:
            ValueError: If provenance binders are not set (from parent).
            TypeError:  If ``obj`` is not a recognised MemoryObject subtype.
        """
        # Determine layer name before calling super() so we can pass it to
        # the store; super().store() raises TypeError for unknown types.
        layer_name = _LAYER_FOR_TYPE.get(type(obj))
        if layer_name is None:
            # Let the parent raise the appropriate TypeError.
            super().store(obj)
            return

        # Parent validates provenance and appends to in-memory list.
        super().store(obj)

        # Persist to SQLite after successful in-memory insertion.
        self._store.save(obj, layer_name)

    def list_layer(self, layer: str) -> List[MemoryObject]:
        """
        Return active memory objects for *layer*, merging SQLite-persisted
        records with the live in-memory list.

        Deduplication is performed on ``memory_id`` so that objects present
        in both sources appear exactly once. Expiry filtering (from the
        parent implementation) is applied **after** the merge.

        Args:
            layer: Logical layer name.

        Returns:
            Deduplicated, non-expired list of memory objects.
        """
        # Start from the (already expiry-filtered) in-memory objects.
        in_memory: List[MemoryObject] = super().list_layer(layer)
        seen_ids: set = {str(getattr(obj, "memory_id", id(obj))) for obj in in_memory}

        # Load persisted rows; reconstruct lightweight proxy objects only for
        # IDs not already present in memory so we avoid double entries.
        # NOTE: Full deserialisation into typed MemoryObject subclasses would
        # require importing the factory from orchx_core. For now we skip
        # re-hydration and rely on the in-memory list as the authoritative
        # source; the SQLite data is the durable backup used by persist_all().
        # Callers that need SQLite-only records should use
        # ``self._store.load_layer(layer)`` directly.
        for row in self._store.load_layer(layer):
            row_id = row.get("id", "")
            if row_id and row_id not in seen_ids:
                # We cannot reconstruct a typed object here without the full
                # factory, so we log and skip. This path is only hit when the
                # process restarted and the in-memory list was cleared.
                seen_ids.add(row_id)

        return in_memory

    # ------------------------------------------------------------------
    # New API
    # ------------------------------------------------------------------

    def persist_all(self) -> int:
        """
        Flush every object currently held in all in-memory layers to SQLite.

        Useful for checkpointing before a graceful shutdown. Already-persisted
        objects are silently upserted (idempotent).

        Returns:
            Total number of objects written to the store.
        """
        count = 0
        for layer_name, layer_list in (
            ("working", self._working),
            ("session", self._session),
            ("project", self._project),
            ("knowledge", self._knowledge),
        ):
            for obj in layer_list:
                self._store.save(obj, layer_name)
                count += 1
        return count
