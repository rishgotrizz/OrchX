#!/usr/bin/env python3
"""
OrchX Doctor — Production Readiness Verification Tool

Usage: python orchx_doctor.py [--json]

Checks:
  [1] SecretVault / ProviderCredentialManager
  [2] Provider Connectivity (8 adapters)
  [3] Storage (SQLite write + read)
  [4] Plugin Registry
  [5] Infrastructure Migrations
  [6] Checkpoint Integrity
  [7] Overall Readiness Score
"""
import asyncio
import json
import sys
import sqlite3
import tempfile
import os
import time

from orchx_runtime.infrastructure_layer import (
    InfrastructureHealthManager,
    ProviderCredentialManager,
    CheckpointManager,
    MigrationManager,
    MigrationVersion,
)
from orchx_runtime.plugin_layer import PluginRegistry
from orchx_runtime.provider_adapters import (
    OpenAIProviderAdapter,
    AnthropicProviderAdapter,
    GoogleGeminiProviderAdapter,
    OllamaProviderAdapter,
    GroqProviderAdapter,
    KimiProviderAdapter,
    NvidiaNimProviderAdapter,
    OpenRouterProviderAdapter,
)
from orchx_core.interfaces.provider_contracts import ProviderRequest


PROVIDER_CONFIGS = [
    ("openai",     OpenAIProviderAdapter,       "gpt-4o"),
    ("anthropic",  AnthropicProviderAdapter,    "claude-3-opus"),
    ("gemini",     GoogleGeminiProviderAdapter,  "gemini-1.5-pro"),
    ("openrouter", OpenRouterProviderAdapter,    "openrouter-llama-3"),
    ("ollama",     OllamaProviderAdapter,        "mistral-7b"),
    ("groq",       GroqProviderAdapter,          "llama3-70b-8192"),
    ("kimi",       KimiProviderAdapter,          "moonshot-v1-32k"),
    ("nvidia",     NvidiaNimProviderAdapter,     "meta/llama3-70b"),
]


class DoctorCheck:
    def __init__(self, name: str):
        self.name = name
        self.passed = False
        self.details = ""
        self.latency_ms = 0.0


async def check_vault(cred: ProviderCredentialManager) -> DoctorCheck:
    c = DoctorCheck("SecretVault")
    try:
        key = cred.get_credential("openai")
        if key and len(key) > 0:
            c.passed = True
            c.details = "Vault accessible, credential retrieved."
        else:
            c.details = "Empty credential returned."
    except Exception as e:
        c.details = f"ERROR: {e}"
    return c


async def check_provider(provider_id: str, AdapterClass, model_id: str, cred: ProviderCredentialManager) -> DoctorCheck:
    c = DoctorCheck(f"Provider:{provider_id}")
    t0 = time.perf_counter()
    try:
        adapter = AdapterClass(cred)
        health = await adapter.get_health()
        c.passed = health.status in ("online", "degraded")
        c.latency_ms = (time.perf_counter() - t0) * 1000
        c.details = f"Status={health.status}, Models={health.supported_models}"
    except Exception as e:
        c.details = f"ERROR: {e}"
    return c


def check_sqlite_storage() -> DoctorCheck:
    c = DoctorCheck("Storage:SQLite")
    try:
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS test_check (id TEXT PRIMARY KEY, val TEXT)")
        cur.execute("INSERT OR REPLACE INTO test_check VALUES ('orchx_doctor', 'ok')")
        conn.commit()
        row = cur.execute("SELECT val FROM test_check WHERE id='orchx_doctor'").fetchone()
        conn.close()
        os.unlink(db_path)
        if row and row[0] == "ok":
            c.passed = True
            c.details = "SQLite read/write cycle successful."
        else:
            c.details = "Read returned unexpected value."
    except Exception as e:
        c.details = f"ERROR: {e}"
    return c


def check_plugin_registry() -> DoctorCheck:
    c = DoctorCheck("PluginRegistry")
    try:
        registry = PluginRegistry()
        # Attempt to load builtin plugins if available
        try:
            from orchx_runtime.builtin_plugins import register_builtin_plugins
            register_builtin_plugins(registry)
            count = len(registry.plugins)
            c.passed = count > 0
            c.details = f"{count} built-in plugins registered."
        except ImportError:
            c.passed = True
            c.details = "Registry healthy (0 built-in plugins — builtin_plugins module not found)."
    except Exception as e:
        c.details = f"ERROR: {e}"
    return c


def check_migrations() -> DoctorCheck:
    c = DoctorCheck("MigrationManager")
    try:
        mgr = MigrationManager()
        v = MigrationVersion(
            version_id="doctor-check-v1",
            description="doctor health check migration",
            schema_hash="xyz",
        )
        result = mgr.apply_migration(v)
        c.passed = result is True
        c.details = f"Migration applied. Total tracked: {len(mgr.applied_versions)}"
    except Exception as e:
        c.details = f"ERROR: {e}"
    return c


def check_checkpoints() -> DoctorCheck:
    c = DoctorCheck("CheckpointManager")
    try:
        mgr = CheckpointManager()
        cp = mgr.create_checkpoint(event_offset=1)
        is_valid = mgr.validate_recovery(cp)
        c.passed = cp.is_validated and is_valid
        c.details = f"Checkpoint {cp.checkpoint_id} created and validated."
    except Exception as e:
        c.details = f"ERROR: {e}"
    return c


def compute_readiness_score(checks: list) -> dict:
    total = len(checks)
    passed = sum(1 for c in checks if c.passed)
    
    categories = {
        "providers": [c for c in checks if c.name.startswith("Provider")],
        "storage": [c for c in checks if "Storage" in c.name or "Migration" in c.name],
        "plugins": [c for c in checks if "Plugin" in c.name],
        "vault": [c for c in checks if "Vault" in c.name],
        "checkpoints": [c for c in checks if "Checkpoint" in c.name],
    }
    
    cat_scores = {}
    for cat, cat_checks in categories.items():
        if cat_checks:
            cat_scores[cat] = round(sum(1 for c in cat_checks if c.passed) / len(cat_checks) * 100)
        else:
            cat_scores[cat] = 0
    
    overall = round(passed / total * 100) if total > 0 else 0
    
    return {
        "overall_percent": overall,
        "total_checks": total,
        "passed_checks": passed,
        "category_scores": cat_scores,
        "remaining_actions": [c.name for c in checks if not c.passed],
    }


async def main():
    output_json = "--json" in sys.argv

    cred = ProviderCredentialManager()
    all_checks = []

    if not output_json:
        print("\n" + "=" * 60)
        print("  ORCHX DOCTOR — Production Readiness Report")
        print("=" * 60 + "\n")

    # [1] Vault
    c = await check_vault(cred)
    all_checks.append(c)
    if not output_json:
        icon = "✅" if c.passed else "❌"
        print(f"  {icon}  {c.name:40s} {c.details}")

    # [2] Providers (run concurrently)
    provider_tasks = [
        check_provider(pid, Cls, mid, cred)
        for pid, Cls, mid in PROVIDER_CONFIGS
    ]
    provider_checks = await asyncio.gather(*provider_tasks)
    for c in provider_checks:
        all_checks.append(c)
        if not output_json:
            icon = "✅" if c.passed else "❌"
            lat = f"[{c.latency_ms:.0f}ms]" if c.latency_ms > 0 else ""
            print(f"  {icon}  {c.name:40s} {c.details} {lat}")

    # [3] Storage
    c = check_sqlite_storage()
    all_checks.append(c)
    if not output_json:
        icon = "✅" if c.passed else "❌"
        print(f"  {icon}  {c.name:40s} {c.details}")

    # [4] Plugin Registry
    c = check_plugin_registry()
    all_checks.append(c)
    if not output_json:
        icon = "✅" if c.passed else "❌"
        print(f"  {icon}  {c.name:40s} {c.details}")

    # [5] Migrations
    c = check_migrations()
    all_checks.append(c)
    if not output_json:
        icon = "✅" if c.passed else "❌"
        print(f"  {icon}  {c.name:40s} {c.details}")

    # [6] Checkpoints
    c = check_checkpoints()
    all_checks.append(c)
    if not output_json:
        icon = "✅" if c.passed else "❌"
        print(f"  {icon}  {c.name:40s} {c.details}")

    # [7] Score
    score = compute_readiness_score(all_checks)

    if output_json:
        report = {
            "checks": [{"name": c.name, "passed": c.passed, "details": c.details} for c in all_checks],
            "score": score,
        }
        print(json.dumps(report, indent=2))
    else:
        print("\n" + "=" * 60)
        print(f"  Production Readiness Score: {score['overall_percent']}%")
        print(f"  Checks Passed: {score['passed_checks']}/{score['total_checks']}")
        print("\n  Category Breakdown:")
        for cat, pct in score["category_scores"].items():
            bar = "█" * (pct // 10) + "░" * (10 - pct // 10)
            print(f"    {cat:15s} [{bar}] {pct}%")
        if score["remaining_actions"]:
            print("\n  Remaining Actions:")
            for action in score["remaining_actions"]:
                print(f"    ⚠️  {action}")
        print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
