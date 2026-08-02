import asyncio
import os
import json
import time
import sys
from traceback import format_exc

sys.path.insert(0, os.path.abspath("packages/orchx-core"))
sys.path.insert(0, os.path.abspath("packages/orchx-runtime"))

from orchx_runtime.vault import SQLiteSecretVault, SecretVaultAdapter
from orchx_runtime.infrastructure_layer import ProviderCredentialManager
from orchx_core.interfaces.provider_contracts import ProviderRequest
from orchx_runtime.provider_adapters import (
    OpenAIProviderAdapter,
    AnthropicProviderAdapter,
    GoogleGeminiProviderAdapter,
    OpenRouterProviderAdapter,
    OllamaProviderAdapter,
    GroqProviderAdapter,
    KimiProviderAdapter,
    NvidiaNimProviderAdapter
)

ADAPTER_CLASSES = [
    OpenAIProviderAdapter,
    AnthropicProviderAdapter,
    GoogleGeminiProviderAdapter,
    OpenRouterProviderAdapter,
    OllamaProviderAdapter,
    GroqProviderAdapter,
    KimiProviderAdapter,
    NvidiaNimProviderAdapter
]

FALLBACK_MODELS = {
    "openai": "gpt-4o-mini",
    "anthropic": "claude-3-haiku-20240307",
    "gemini": "gemini-1.5-flash",
    "openrouter": "openrouter/auto",
    "ollama": "llama3",
    "groq": "llama3-8b-8192",
    "kimi": "moonshot-v1-8k",
    "nvidia": "meta/llama3-8b-instruct"
}

async def verify_provider(adapter, cred_manager):
    provider_id = adapter.provider_info.id
    
    report = {
        "provider_name": adapter.metadata.display_name,
        "provider_id": provider_id,
        "credentials": "MISSING CREDENTIALS",
        "auth_status": "NOT TESTED",
        "model_discovery": "NOT SUPPORTED",
        "chat_completion": "NOT TESTED",
        "streaming": "NOT SUPPORTED",
        "latency_ms": 0.0,
        "telemetry": {},
        "billing": {},
        "circuit_breaker": "PASS",
        "overall": "FAIL",
        "error": None
    }
    
    # Check credentials
    if not adapter.metadata.authentication_required:
        report["credentials"] = "NOT REQUIRED"
    else:
        try:
            cred = cred_manager.get_credential(provider_id)
            report["credentials"] = "PASS"
        except ValueError:
            report["credentials"] = "MISSING CREDENTIALS"
            report["overall"] = "MISSING CREDENTIALS"
            return report
        except Exception as e:
            report["credentials"] = f"FAIL (Error: {str(e)})"
            report["overall"] = "FAIL"
            return report

    # Model Discovery
    models_found = []
    if adapter.metadata.model_discovery_endpoint is not None:
        try:
            models = await adapter._fetch_models()
            if models:
                report["model_discovery"] = f"PASS ({len(models)} models found)"
                models_found = models
            else:
                report["model_discovery"] = "WARNING (0 models returned)"
        except Exception as e:
            report["model_discovery"] = f"FAIL (Error: {str(e)})"
            report["error"] = format_exc()
            report["auth_status"] = f"FAIL ({str(e)})"
            return report

    report["auth_status"] = "PASS"

    test_model = FALLBACK_MODELS.get(provider_id)
    if models_found:
        test_model = models_found[0].id

    if not test_model:
        report["chat_completion"] = "FAIL (No model available to test)"
        return report

    # Chat Completion
    request = ProviderRequest(
        model_id=test_model,
        messages=[{"role": "user", "content": "Reply with the single word: OK"}],
        max_tokens=10
    )
    
    try:
        t0 = time.time()
        response = await adapter.call(request)
        latency = (time.time() - t0) * 1000
        
        report["chat_completion"] = "PASS"
        report["latency_ms"] = round(latency, 2)
        report["telemetry"] = {
            "latency_ms": response.usage.latency_ms,
            "retry_count": response.usage.retry_count,
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens
        }
        report["billing"] = {
            "estimated_cost": response.usage.estimated_cost
        }
    except Exception as e:
        report["chat_completion"] = f"FAIL ({str(e)})"
        report["error"] = format_exc()
        return report

    # Streaming
    if "streaming" in adapter.metadata.supported_capabilities:
        try:
            chunks = []
            stream_start = time.time()
            async for chunk in adapter.stream(request):
                chunks.append(chunk)
            
            if len(chunks) > 0:
                report["streaming"] = "PASS"
            else:
                report["streaming"] = "FAIL (No chunks received)"
        except Exception as e:
            report["streaming"] = f"FAIL ({str(e)})"
            report["error"] = format_exc()

    if adapter.transport.circuit_breaker.state == "closed":
        report["circuit_breaker"] = "PASS"
    else:
        report["circuit_breaker"] = "FAIL"

    report["overall"] = "PASS"
    return report

async def main():
    vault_db_path = os.environ.get("ORCHX_DB_PATH", "runtime.db")
    vault = SQLiteSecretVault(db_path=vault_db_path)
    vault_adapter = SecretVaultAdapter(vault)
    cred_manager = ProviderCredentialManager(vault_adapter)
    
    adapters = [AdapterClass(cred_manager) for AdapterClass in ADAPTER_CLASSES]
    
    print("============================================================")
    print("OBJECTIVE 5 & 7 - PRE-FLIGHT VALIDATION & LIVE READINESS")
    print("============================================================")
    print(f"{'Provider':<20} | {'Credential Present':<20} | {'Auth Required':<15} | {'Verification Enabled':<20} | {'Status'}")
    print("-" * 110)
    
    pre_flight = {}
    for adapter in adapters:
        name = adapter.metadata.display_name
        req = adapter.metadata.authentication_required
        ver_en = adapter.metadata.verification_enabled
        prod = adapter.metadata.production_enabled
        
        if not prod:
            continue
            
        cred_present = "N/A"
        status = "READY"
        
        if req:
            try:
                cred_manager.get_credential(adapter.provider_info.id)
                cred_present = "YES"
                status = "READY FOR LIVE VERIFICATION"
            except ValueError:
                cred_present = "NO"
                status = "MISSING CREDENTIALS"
            except Exception:
                cred_present = "ERROR"
                status = "ERROR"
        else:
            status = "READY FOR LIVE VERIFICATION"
                
        print(f"{name:<20} | {cred_present:<20} | {str(req):<15} | {str(ver_en):<20} | {status}")
        pre_flight[adapter.provider_info.id] = status
        
    print("\nPre-flight validation complete. Platform is prepared. Stopping before live verification as instructed.")
    return

if __name__ == "__main__":
    asyncio.run(main())
