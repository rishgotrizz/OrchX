import contextlib
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
from orchx_api.api.v1 import auth, plugins, dashboard, preview, suggestions, vault_routes
from orchx_runtime.infrastructure_layer import ProviderCredentialManager

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    # Assemble Runtime Kernel configuration
    config = KernelConfig(
        project_name="OrchX AI OS",
        security=SecurityConfig(
            secret_key="32b217e651e069273fb89ef0673d32efde6db36d0dbef1e83161c6b12a8be51e",
            enable_sandbox=True
        ),
        runtime=RuntimeConfig(
            plugin_dir="plugins"
        )
    )

    # Initialize Vault and set global for routes
    vault_routes.global_cred_manager = ProviderCredentialManager()

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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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


@app.get("/healthz", status_code=200, tags=["health"])
async def root_health_check():
    """Verify kernel HTTP server availability."""
    return {"status": "online"}
