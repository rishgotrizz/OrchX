import contextlib
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from orchx_core.config import KernelConfig, SecurityConfig, RuntimeConfig
from orchx_runtime.bus import InMemoryEventBus
from orchx_runtime.context import KernelContext
from orchx_runtime.agent_registry import AgentRegistry
from orchx_runtime.capability_registry import CapabilityRegistry
from orchx_runtime.provider_registry import ProviderRegistry
from orchx_runtime.tool_registry import ToolRegistry
from orchx_runtime.workflow_registry import WorkflowRegistry
from orchx_runtime.kernel import Kernel

# We import the route blueprints from the current package context
from orchx_api.api.v1 import auth, plugins, dashboard, preview, suggestions, vault_routes, runtime
from orchx_runtime.infrastructure_layer import ProviderCredentialManager

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    from orchx_api.core.auth import SECRET_KEY as auth_secret_key
    # Assemble Runtime Kernel configuration
    config = KernelConfig(
        project_name="OrchX AI OS",
        security=SecurityConfig(
            secret_key=auth_secret_key,
            enable_sandbox=True
        ),
        runtime=RuntimeConfig(
            plugin_dir="plugins"
        )
    )

    # Initialize Vault and set global for routes
    from orchx_runtime.vault import SQLiteSecretVault, SecretVaultAdapter
    db_path = os.environ.get("ORCHX_DB_PATH", "runtime.db")
    vault = SQLiteSecretVault(db_path)
    vault_adapter = SecretVaultAdapter(vault)
    cred_manager = ProviderCredentialManager(vault_adapter)
    vault_routes.global_cred_manager = cred_manager

    # Instantiate decoupled kernel subsystems
    event_bus = InMemoryEventBus()
    provider_registry = ProviderRegistry()
    agent_registry = AgentRegistry()
    tool_registry = ToolRegistry()
    workflow_registry = WorkflowRegistry()
    capability_registry = CapabilityRegistry()

    # Create contextual injection container
    context = KernelContext(
        config=config,
        event_bus=event_bus,
        provider_registry=provider_registry,
        agent_registry=agent_registry,
        tool_registry=tool_registry,
        workflow_registry=workflow_registry,
        capability_registry=capability_registry
    )

    # Initialize kernel orchestrator
    kernel = Kernel(context)
    app.state.kernel = kernel
    app.state.kernel_context = context

    # Register default providers in context's provider_registry
    from orchx_runtime.provider_manager import ProviderManager
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
    
    provider_registry.register(OpenAIProviderAdapter(cred_manager))
    provider_registry.register(AnthropicProviderAdapter(cred_manager))
    provider_registry.register(GoogleGeminiProviderAdapter(cred_manager))
    provider_registry.register(OpenRouterProviderAdapter(cred_manager))
    provider_registry.register(OllamaProviderAdapter(cred_manager))
    provider_registry.register(GroqProviderAdapter(cred_manager))
    provider_registry.register(KimiProviderAdapter(cred_manager))
    provider_registry.register(NvidiaNimProviderAdapter(cred_manager))
    
    # Register ProviderManager as a kernel service
    provider_manager = ProviderManager()
    context.register_service("provider_manager", provider_manager)

    # Boot OS Kernel
    await kernel.start()
    
    yield
    # Graceful Shutdown
    await kernel.stop()


app = FastAPI(
    title="OrchX Kernel Engine API",
    description="Universal interface and visualization layer for OrchX. Strict OpenAPI compliant schemas.",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    lifespan=lifespan,
)

# CORS
import os
allowed_origins = [
    origin.strip()
    for origin in os.environ.get("ORCHX_ALLOWED_ORIGINS", "http://localhost:3000").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routing
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(plugins.router, prefix="/api/v1/plugins", tags=["plugins"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])
app.include_router(preview.router, prefix="/api/v1/preview", tags=["preview"])
app.include_router(suggestions.router, prefix="/api/v1/suggestions", tags=["suggestions"])
app.include_router(vault_routes.router, prefix="/api/v1", tags=["vault"])
app.include_router(runtime.router, prefix="/api/v1", tags=["runtime"])


@app.get("/healthz", status_code=200, tags=["health"])
async def root_health_check():
    """Verify kernel HTTP server availability."""
    return {"status": "online"}
